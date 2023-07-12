import os
import random
import subprocess
from matplotlib import pyplot as plt
import scipy.signal as signal
import numpy as np
import cv2
import pywt
import scipy.fftpack as sp
from app.key import get_key, write_key
from tqdm import tqdm





def cfold(z):
    z_folded = (z.real % 1) + (z.imag % 1) * 1j
    return z_folded

def embed_watermark(section, logo,a,b,z1,z2):
    section = cv2.cvtColor(section,cv2.COLOR_RGB2YCrCb)
    R = section[:, :, 0]
    G = section[:, :, 1]
    B = section[:, :, 2]

    # Apply CT to each channel
    wavelet1 = 'Haar'
    coeffs_R1 = pywt.dwt2(R, wavelet1)
    coeffs_G1 = pywt.dwt2(G, wavelet1)
    coeffs_B1 = pywt.dwt2(B, wavelet1)
    
    # Extract LL sub-band of each channel
    LL_R1, (LH_R1, HL_R1, HH_R1) = coeffs_R1
    LL_G1, (LH_G1, HL_G1, HH_G1) = coeffs_G1
    LL_B1, (LH_B1, HL_B1, HH_B1) = coeffs_B1

    wavelet2 = 'db16'
    coeffs_R2 = pywt.dwt2(LL_R1, wavelet2)
    coeffs_G2 = pywt.dwt2(LL_G1, wavelet2)
    coeffs_B2 = pywt.dwt2(LL_B1, wavelet2)

    LL_R2, (LH_R2, HL_R2, HH_R2) = coeffs_R2
    LL_G2, (LH_G2, HL_G2, HH_G2) = coeffs_G2
    LL_B2, (LH_B2, HL_B2, HH_B2) = coeffs_B2

    
    # Combine LL sub-bands of each channel
    LL = cv2.merge((LL_R2, LL_G2, LL_B2))

    w_x, w_y = logo.shape[0], logo.shape[1]
    ll_x, ll_y = LL.shape[0], LL.shape[1]

    mask = np.zeros(shape=((ll_x//4),(ll_y//4),3))

    for i in range(w_x):
        for j in range(w_y):
            while True:
                z3 = (z1 - a * ((np.sin(z2)*np.sin(z1))/np.cos(z1)))
                z4 = (z2 - b * ((np.sin(z1)*np.sin(z2))/np.cos(z2 )))

                z3 = cfold(z3)
                z4 = cfold(z4)
                
                x = int(np.floor(z3.real*10**14) % (ll_x//4))
                y = int(np.floor(z3.imag*10**14) % (ll_y//4))
                c = int(np.floor(z4.real*10**14) % 3)

                z1 = z3
                z2 = z4
                if mask[x][y][c] == 0 :
                    break

            # EK = z2.imag > 0.5

            # logo[i,j] = logo[i,j] ^ EK

            B = LL[x*4 : x*4+4 , y*4 : y*4+4 , c]

            # u, s, v = np.linalg.svd(B)

            # avg = ((np.abs(u[0,0])+ np.abs(u[1,0]))/2)

            # T = 0.025
            # if logo[i,j] == 0:
            #     temp = np.abs(np.abs(u[0,0]) - np.abs(u[1,0]))
            #     if np.abs(u[0,0]) > np.abs(u[1,0]) and temp < T:
            #         u[0,0] = np.sign(u[0,0]) * (avg + (T/2))
            #         u[1,0] = np.sign(u[1,0]) * (avg - (T/2))
                
            # else:
            #     temp = np.abs(np.abs(u[1,0]) - np.abs(u[0,0]))
            #     if np.abs(u[0,0]) < np.abs(u[1,0] and temp > T):
            #         u[0,0] = np.sign(u[0,0]) * (avg - (T/2))
            #         u[1,0] = np.sign(u[1,0]) * (avg + (T/2))

            # B = u * s * v
            
            # T = 0.5
            # N = B.shape[0]
            # M = B.shape[1]

            # Convert RGB block to grayscale
            

            dct_block = sp.dct(sp.dct(B.T, norm='ortho').T, norm='ortho')

            # if logo[i,j] == 255:
            #     dct_block[1,2] = 5
            # else:
            #     dct_block[1,2] = -5


            alpha = 20
            beta = 2*alpha
            gamma = 3*alpha
            delta = 4*alpha
            echo = 5*alpha

            coefficient = [(2,0), (1,1), (0,2), (0,3), (1,2), (2,1)]

            if logo[i,j] == 255:
                # for u in range(1,1):
                #     for v in range(1,3):
                for u,v in coefficient:
                        if np.mod(dct_block[u,v], delta) <= alpha:
                            dct_block[u,v] = dct_block[u,v] - np.mod(dct_block[u,v], delta) - alpha
                        else:
                            dct_block[u,v] = dct_block[u,v] - np.mod(dct_block[u,v], delta) + gamma
            elif logo[i,j] == 0:
                # for u in range(1,3):
                #     for v in range(1,3):
                for u,v in coefficient:
                        if np.mod(dct_block[u,v], delta) >= gamma:
                            dct_block[u,v] = dct_block[u,v] - np.mod(dct_block[u,v], delta) + echo
                        else:
                            dct_block[u,v] = dct_block[u,v] - np.mod(dct_block[u,v], delta) + alpha

            

            idct_block = sp.idct(sp.idct(dct_block.T, norm='ortho').T, norm='ortho')

            LL[x*4 : x*4+4 , y*4 : y*4+4 , c] = idct_block[:,:]
            # LL[x*4 : x*4+4 , y*4 : y*4+4 , c] = B
            mask[x][y][c] = 1

            

    LowPassR = LL[:,:,0]
    LowPassG = LL[:,:,1]
    LowPassB = LL[:,:,2]

    # Reconstruct the image from wavelet coefficients and sub-bands
    coeffs_R2 = (LowPassR, (LH_R2, HL_R2, HH_R2))
    recon_img_R2 = pywt.idwt2(coeffs_R2, wavelet2)

    coeffs_G2 = (LowPassG, (LH_G2, HL_G2, HH_G2))
    recon_img_G2 = pywt.idwt2(coeffs_G2, wavelet2)

    coeffs_B2 = (LowPassB, (LH_B2, HL_B2, HH_B2))
    recon_img_B2 = pywt.idwt2(coeffs_B2, wavelet2)

    coeffs_R1 = (recon_img_R2, (LH_R1, HL_R1, HH_R1))
    recon_img_R = pywt.idwt2(coeffs_R1, wavelet1)

    coeffs_G1 = (recon_img_G2, (LH_G1, HL_G1, HH_G1))
    recon_img_G = pywt.idwt2(coeffs_G1, wavelet1)

    coeffs_B1 = (recon_img_B2, (LH_B1, HL_B1, HH_B1))
    recon_img_B = pywt.idwt2(coeffs_B1, wavelet1)


    section[:, :, 2] = recon_img_B
    section[:, :, 1] = recon_img_G
    section[:, :, 0] = recon_img_R

    frame = cv2.cvtColor(section,cv2.COLOR_YCrCb2RGB)

    z1 = z3
    z2 = z4

    return z1,z2,frame


def extract_watermark(section,a,b,z1,z2):
    section = cv2.cvtColor(section,cv2.COLOR_RGB2YCrCb)
    R = section[:, :, 0]
    G = section[:, :, 1]
    B = section[:, :, 2]

    # Apply CT to each channel
    wavelet1 = 'Haar'
    coeffs_R1 = pywt.dwt2(R, wavelet1)
    coeffs_G1 = pywt.dwt2(G, wavelet1)
    coeffs_B1 = pywt.dwt2(B, wavelet1)
    
    # Extract LL sub-band of each channel
    LL_R1, (LH_R1, HL_R1, HH_R1) = coeffs_R1
    LL_G1, (LH_G1, HL_G1, HH_G1) = coeffs_G1
    LL_B1, (LH_B1, HL_B1, HH_B1) = coeffs_B1

    wavelet2 = 'db16'
    coeffs_R2 = pywt.dwt2(LL_R1, wavelet2)
    coeffs_G2 = pywt.dwt2(LL_G1, wavelet2)
    coeffs_B2 = pywt.dwt2(LL_B1, wavelet2)

    LL_R2, (LH_R2, HL_R2, HH_R2) = coeffs_R2
    LL_G2, (LH_G2, HL_G2, HH_G2) = coeffs_G2
    LL_B2, (LH_B2, HL_B2, HH_B2) = coeffs_B2

    
    # Combine LL sub-bands of each channel
    LL = cv2.merge((LL_R2, LL_G2, LL_B2))

    w_x, w_y = 32,32
    ll_x, ll_y = LL.shape[0], LL.shape[1]

    mask = np.zeros(shape=((ll_x//4),(ll_y//4),3))
    watermark = np.zeros(shape=(32,32))

    for i in range(w_x):
        for j in range(w_y):
            while True:
                z3 = (z1 - a * ((np.sin(z2)*np.sin(z1))/np.cos(z1)))
                z4 = (z2 - b * ((np.sin(z1)*np.sin(z2))/np.cos(z2 )))

                z3 = cfold(z3)
                z4 = cfold(z4)
                
                x = int(np.floor(z3.real*10**14) % (ll_x//4))
                y = int(np.floor(z3.imag*10**14) % (ll_y//4))
                c = int(np.floor(z4.real*10**14) % 3)

                z1 = z3
                z2 = z4
                if mask[x][y][c] == 0 :
                    break
            

            B1 = LL[x*4 : x*4+4 , y*4 : y*4+4 , c]
            dct_block1 = sp.dct(sp.dct(B1.T, norm='ortho').T, norm='ortho')

            # u = dct_block1[1,2] - dct_block2[1,2]
            
            # if dct_block1[1,2] > 0:
            #     watermark[i,j] = 255
            # else:
            #     watermark[i,j] = 0

            alpha = 20
            beta = 2*alpha
            gamma = 3*alpha
            delta = 4*alpha
            echo = 5*alpha

            coefficient = [(2,0), (1,1), (0,2), (0,3), (1,2), (2,1)]
            avg = 0
            # for u in range(1,3):
                # for v in range(1,3):
            for u,v in coefficient:
                    if np.mod(dct_block1[u,v],delta) > beta:
                        avg += 255
                    else:
                        avg += 0

            avg /= len(coefficient)
            # avg /= 4

            watermark[i,j] = 255 if avg >= 127.5 else 0
            
            

            # u,s,v = np.linalg.svd(B)

            # if np.abs(u[0,0]) > np.abs(u[1,0]):
            #     watermark[i,j] = 0
            # else:
            #     watermark[i,j] = 255

            # # EK = z2.imag > 0.5
            # # watermark[i,j] = wa
            
            mask[x][y][c] = 1

     

    z1 = z3
    z2 = z4

    return z1,z2,watermark



def embed(logo, input_file):
    clip = cv2.VideoCapture("input/"+input_file)
    fps = round(clip.get(cv2.CAP_PROP_FPS))
    clip_w = clip.get(cv2.CAP_PROP_FRAME_WIDTH)
    clip_h = clip.get(cv2.CAP_PROP_FRAME_HEIGHT)
    f = round(clip.get(cv2.CAP_PROP_FRAME_COUNT))

    # Extract the audio from the video
    audio_file = "audio/"+input_file[:-3]+"audio.aac"
    if not os.path.exists(audio_file):
        subprocess.call(["ffmpeg", "-i", "input/"+input_file, "-vn", "-acodec", "copy", audio_file])

    # Creating the temporal codes
    k = int(str(f**2)[:2])
    '''Note : Try to find d which will include 30 bit'''
    delay = 5
    d = round(clip.get(cv2.CAP_PROP_FRAME_COUNT))
    #temporal_codes = rm.random_masking_function(logo,d)


    
    #plt.imshow(temporal_codes[0],cmap="gray")
    #plt.show()
    
    # r=rm.averaging(temporal_codes,f//key)
    # r = (r+0.1)/0.5
    #plt.imshow(r,cmap="gray")
    #plt.show()

    # Create the output file
    output_file = "output/"+"final_"+input_file[:-3]+"mkv"
    w_clip = int(clip.get(cv2. CAP_PROP_FRAME_WIDTH ))
    h_clip = int(clip.get(cv2. CAP_PROP_FRAME_HEIGHT ))
    # fourcc = int(clip.get(cv2. CAP_PROP_FOURCC))
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    print(fourcc, cv2.VideoWriter_fourcc(*'MJPG'))
    file = cv2.VideoWriter(output_file, fourcc, fps, (w_clip, h_clip),isColor=True)
    ret = True
    i=j=0
    m=1


    key = get_key(input_file)
    key.sort()
    
    a = 2
    b = 3
    z1 = complex(0.4,0.6)
    z2 = complex(0.4,0.6)

    for i in tqdm(range(d), desc="Embedding...", colour="green"):
        ret,frame = clip.read()

        # if ret :
        #     frame = frame[ : , int(h_clip*0.05) : int(h_clip*0.9) , : ]

        if ret == False:
            break

        flag = True
        section = np.copy(frame)

        if(j<len(key) and  ret and i==key[j]):
            if np.mean(frame[:,:,:]) == 0:
                key.pop(j)
            else:
                z3,z4 = z1,z2
                z1, z2, frame[:,:,:] = embed_watermark(frame, logo,a,b,z1,z2)

                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ref_gray = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)

                psnr_value = cv2.PSNR(frame_gray, ref_gray)

                # if psnr_value < 30:
                #     # file.write(section)
                #     key.pop(j)
                #     flag = False
                # else:
                #     j+=1
                #     print(((j)/len(key))*100)
                #     z1,z2,extracted_watermark = extract_watermark(frame,a,b,z3,z4)

                j+=1
                # print(((j)/len(key))*100)   
                # tqdm.write(f"Progress: {j}/{len(key)}")                    
            
            
                
                        
        if flag :    
            file.write(frame)
        else:
            file.write(section)
    
    file.release()

    #subprocess.call(["ffmpeg", "-i", "output/"+"final_"+input_file[:-3]+"mkv", "-i", audio_file, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "output/"+input_file[:-4]+"_final.mkv"])

    subprocess.call(['ffmpeg', '-i', "output/"+"final_"+input_file[:-3]+"mkv", '-i' ,audio_file ,'-c:v', "copy", "-c:a", 'aac', '-map', '0:v:0', '-map', '1:a:0',"output/"+input_file[:-4]+"_final.mkv"])




    if os.path.exists("output/"+"final_"+input_file[:-4]+".mkv"):
        os.remove("output/"+"final_"+input_file[:-4]+".mkv")


    write_key(input_file,key)


def Extract(input_file):
    output_file = "output/"+input_file[:-4]+"_final.mkv"
    file = cv2.VideoCapture(output_file)
    d = round(file.get(cv2.CAP_PROP_FRAME_COUNT))
    key = get_key(input_file)
    key.sort()
    # input_file = "input/theif.mp4"
    # clip = cv2.VideoCapture(input_file)
    a = 2
    b = 3
    z1 = complex(0.4,0.6)
    z2 = complex(0.4,0.6)

    ret1 = ret2 = True
    i=j=0
    watermark = []
    for i in tqdm(range(d), desc="Extracting...", colour="red"):
        ret1,frame1 = file.read()

        if ret1 == False:
            break


        if(j<len(key) and i==key[j] and ret1):
            z1,z2,extracted_watermark = extract_watermark(frame1,a,b,z1,z2)
            
            watermark.append(extracted_watermark)
            # plt.imshow(extracted_watermark,cmap="gray")
            # plt.show()
            # print(((j+1)/len(key))*100)

            
                
                        

            j+=1
    
    file.release()

    accumulated = np.zeros(shape=(32,32))
    for i in range(len(watermark)):
        accumulated += watermark[i]

    accumulated//=len(key)

    blurred = cv2.GaussianBlur(accumulated, (5,5), 1.5)
    sharpened = cv2.addWeighted(accumulated, 1.5, blurred, -0.5, 0)

    return sharpened


def gen_num(n):
    numbers = list(range(n+1))
    random.shuffle(numbers)
    return numbers[:n//16]

    # img = cv2.convertScaleAbs(sharpened)
    # filtered_img = cv2.bilateralFilter(img, 5, 75, 75)
    # plt.imshow(sharpened,cmap="gray")
    # plt.show()
    # _, result = cv2.threshold(sharpened, 127.5, 255, cv2.THRESH_BINARY)
    # plt.imshow(result,cmap="gray")
    # plt.show()

