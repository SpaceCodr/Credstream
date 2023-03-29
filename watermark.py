import m3u8
import sys

if len(sys.argv)>1:
    file=sys.argv[1]
else:
    file='hope'

# Load the HLS manifest file
manifest = m3u8.load('static/videos/'+file+'.m3u8')

# Get the list of segments from the manifest file
segments = manifest.segments
print(segments)

# Loop through each segment and add the watermark

# Save the modified manifest file
with open('tempfs/'+file+'.m3u8', 'w') as f:
    f.write(manifest.dumps())
