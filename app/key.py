
import csv
import os
import random
import cv2
import pyAesCrypt


def get_key(input_file):
    # Creating the key
    clip = cv2.VideoCapture("input/"+input_file)
    d = round(clip.get(cv2.CAP_PROP_FRAME_COUNT))
    try:
        # Set the encryption parameters
        buffer_size = 64 * 1024
        password = 'my_password'
        # Try to decrypt the file
        if not os.path.exists("keys/"+input_file[:-3]+"csv"):
            raise FileNotFoundError
        pyAesCrypt.decryptFile("keys/"+input_file[:-3]+"csv", "keys/"+input_file[:-3]+"txt", password, buffer_size)
        key = []
        with open("keys/"+input_file[:-3]+"txt", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                key.extend([int(val) for val in row if val.isdigit()])

    except FileNotFoundError:
        # If the file does not exist, create it
        key = gen_num(d)
        pathu="keys/"
        # if not os.path.exists(pathu):
        #     os.makedirs(pathu)
        with open("keys/"+input_file[:-3]+"txt", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(key)
        # Set the encryption parameters
        buffer_size = 64 * 1024
        password = 'my_password'

        # Encrypt the files
        pyAesCrypt.encryptFile("keys/"+input_file[:-3]+"txt", "keys/"+input_file[:-3]+"csv", password, buffer_size)
    finally:
        # Delete the unencrypted files
        if os.path.exists("keys/"+input_file[:-3]+"txt"):
            os.remove("keys/"+input_file[:-3]+"txt")
    
    return key

def write_key(input_file, key):
    try:
        # Set the encryption parameters
        buffer_size = 64 * 1024
        password = 'my_password'
        # Try to decrypt the file
        if not os.path.exists("keys/"+input_file[:-3]+"csv"):
            raise FileNotFoundError
        pyAesCrypt.decryptFile("keys/"+input_file[:-3]+"csv", "keys/"+input_file[:-3]+"txt", password, buffer_size)
        key = []
        with open("keys/"+input_file[:-3]+"txt", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                key.extend([int(val) for val in row if val.isdigit()])

    except FileNotFoundError:
        print("FileNotFoundError")
    
    if os.path.exists("keys/"+input_file[:-3]+"txt"):
        os.remove("keys/"+input_file[:-3]+"txt")
    
def gen_num(n):
    numbers = list(range(n+1))
    random.shuffle(numbers)
    return numbers[:n//16]