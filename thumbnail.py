from moviepy.video.io.VideoFileClip import VideoFileClip
import sys
import imageio
from PIL import Image,ImageDraw,ImageFont

if len(sys.argv)>1:
    file=sys.argv[1]
    filein=file+'.mp4'
else:
    file='hope'
    filein='hope.mkv'
# Load the video file
clip = VideoFileClip("prevideos/"+filein)

# Extract a frame at the 10-second mark
thumbnail = clip.get_frame(10)


# Save the thumbnail as an image file
# imageio.imwrite("metapic/"+file+'.jpg', thumbnail)
img=Image.open('metapic/'+file+'.jpg')
width,height=img.size
m=ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", 310)
m.text((350,height-500),text=file.upper(),font=font,fill=(240,240,255,128),stroke_width=4)
img.save('metapic/title/'+file+'.jpg')

