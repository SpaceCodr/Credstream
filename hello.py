from flask import Flask, request, send_file
from watermarking import watermark_video

app = Flask(__name__)

@app.route('/video/<user_id>/<video_name>')
def stream_video(user_id, video_name):
    # Retrieve the requested video file
    video_path = f"/path/to/videos/{video_name}.mp4"
    
    # Create a unique output file path for the watermark-embedded video segment
    output_path = f"/path/to/watermarked_videos/{user_id}_{video_name}.mp4"
    
from io import BytesIO
from PIL import Image

class Watermark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_bytes = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='watermarks')

@app.route('/<segment>')
@login_required
def serve_segment(segment):
    user = current_user
    app.logger.info('received request for ' + str(segment))
    common_path = 'commonsegments\\' + segment
    
    if os.path.exists('commonsegments\\' + segment):
        return send_file(common_path)
    
    open_path = 'embedded\\' + user.username + '\\' + segment
    if os.path.exists(open_path):
        streamed_files[segment] = time.time()
        return send_file(open_path)

    watermark = Watermark.query.filter_by(user_id=user.id).first()
    if not watermark:
        return 'Watermark not found', 404

    watermark_image = Image.open(BytesIO(watermark.image_bytes))
    watermark_image = watermark_image.convert('1')  # convert to black and white image
    watermark_image = watermark_image.resize((64, 64))

    path = "opensegments\\" + segment

    command = ['ffprobe', '-show_entries', 'format=start_time', '-v', 'quiet', '-of', 'csv=p=0', path]

    output = subprocess.check_output(command)
    start_time = float(output.decode('utf-8').strip().splitlines()[0])
    pathin = "input\\" + segment[:-3] + '.mp4'
    subprocess.call(['ffmpeg', '-i', path, '-vcodec', 'copy', '-acodec', 'copy', pathin])

    main.embed(watermark_image, segment[:-3] + '.mp4')
    pathout = "output\\" + segment[:-3] + '_final.mkv'
    pathhpre = "embedded\\" + user.username
    if not os.path.exists(pathhpre):
        os.makedirs(pathhpre)
    pathh = pathhpre + '\\' + segment
    subprocess.call(['ffmpeg', '-i', pathout, '-vcodec', 'copy', '-acodec', 'copy', pathh])
    os.remove(pathout)
    os.remove(pathin)

    start_time = start_time / 2

    subprocess.call(['ffmpeg', '-i', pathh, '-map', '0', '-c', 'copy', '-muxpreload', str(start_time), '-muxdelay', str(start_time), pathh + '_temp.ts'])
    os.remove(pathh)
    os.rename(pathh + '_temp.ts', pathh)

    jeez = pathh
    streamed_files[segment] = time.time()
    return send_file(jeez)

    # If file not found in both folders, return 404 error
    return 'File not found', 404
