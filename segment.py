import sys,datetime,logging
import ffmpeg_streaming2
from ffmpeg_streaming2 import Formats,Bitrate,Representation,Size    

if len(sys.argv) > 1:
    file=sys.argv[1]
    filein=file+'.mp4'
    fileout=file+'.m3u8'
else:
    filein='hope.mkv'
    fileout='hope.m3u8'

videofile=ffmpeg_streaming2.input('prevideos/'+filein)
    
logging.basicConfig(filename='streaming.log', level=logging.NOTSET, format='[%(asctime)s] %(levelname)s: %(message)s')

def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()


    # _360p  = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
# _480p  = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))
_720p  = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))
    
    
hls = videofile.hls(Formats.h264())
hls.representations(_720p)
hls.output('static/videos/'+fileout,monitor=monitor)
# videofile2 = ffmpeg_streaming2.input('static/videos/result_ice_720p.m3u8')

# stream = videofile2.stream2file(Formats.h264())
# stream.output('static/final2.mp4')