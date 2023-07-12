from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import textwrap
import threading
import time
from flask import render_template, request, jsonify, make_response,Response,stream_with_context,send_from_directory
from flask_login import (
    login_user,
    current_user,
    logout_user,
    login_required
)
from werkzeug.security import check_password_hash, generate_password_hash
from app import models
from config import db, bcrypt, login_manager, create_app
from app.models import User,Videos,Watermark
import os
import cv2
import numpy as np
import json
from PIL import Image, ImageDraw, ImageFont
import io
import os
from flask import Flask, send_file, request
import subprocess
# from celery import current_app
import logging
import time
from app import main
import cv2

app = create_app()
app.logger.setLevel(logging.INFO)
secret_cred=1257
STREAM_FOLDER=["embedded"]
DELETE_TIME = 5 * 60 * 60
# DELETE_TIME = 30
# streamed_files = {}

def generate_watermark(cred):
    # Generate watermark image with cred
    # img = Image.new('RGB', (64, 64), (255, 255, 255))
    # img = Image.new('RGB', (64, 64), (0, 0, 0))
    img = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('arial.ttf', 33)
    lines = textwrap.wrap(cred, width=2)
    print(lines)
    y_text = 0
    for line in lines:
        width, height = fnt.getsize(line)
        d.text(((64 - width) / 2, y_text), line, font=fnt,stroke_width=2, fill=(0,0,0,128))
        # d.text(((64 - width) / 2, y_text), line, font=fnt,stroke_width=2, fill=(255,255,255,128))
        y_text += height
    # # Convert image to bytes and return
    # with io.BytesIO() as output:
    #     img.save(output, format="PNG")
    #     img.show()
    #     watermark_bytes = output.getvalue()

    # Save image to file
    filename="wmorg/watermark_org.jpg"
    img.save(filename)
    # Convert image to bytes and return
    with open(filename, 'rb') as f:
        watermark_bytes = f.read()
    return watermark_bytes



@app.route('/api/test')
@login_required
def test_api():
    return jsonify({'message': 'Hello, Flutter!'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(name=data['name'], date_of_birth=data['date_of_birth'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(email=data['email']).first()
    cred=secret_cred+user.id
    watermark_bytes = generate_watermark(str(cred))
    new_watermark = Watermark(user_id=user.id, image_bytes=watermark_bytes)
    db.session.add(new_watermark)
    db.session.commit()
    return make_response(jsonify({'message': 'User created successfully!', 'cred': cred,'name': user.name}),201)

@app.route('/api/list/')
def list():
    users = User.query.all()
    for user in users:
        print(user.email)
        print(user.name)
        print(user.date_of_birth)
    return make_response(jsonify({'message':'Listed users'}),200)

@app.route('/api/deleteallusers/', methods=['DELETE'])
def delete_all_users():
    try:
        # Delete all users from the database
        db.session.query(User).delete()
        db.session.commit()
        return make_response(jsonify({'message': 'All users have been deleted.'}), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': 'Failed to delete all users.'}), 500)


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        print(user.id)
        cred=secret_cred+user.id
        print(cred)
        response_data = {'message': 'Logged in successfully!', 'cred': cred,'name': user.name}
        return make_response(jsonify(response_data), 200)
    else:
        return make_response(jsonify({'message': 'Invalid email or password'}), 401)

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return make_response(jsonify({'message': 'Logged out successfully!'}), 200)

# @app.route('/video/<int:video_id>')
# @login_required
# def video(video_id):
#     video = Videos.query.get_or_404(video_id)
#     videofile = 'static/videos/' + video.title

#     return Response(video_stream.stream(videofile),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/api/video')
# # @login_required
# def videohope():
#     filename = request.args.get('filename')
#     # path=os.path.join('static/videos'+filename)
#     video='static/videos/'+filename
#     def generate():
#         with open(video, 'rb') as video_file:
#             while True:
#                 data = video_file.read(1024 * 1024)
#                 if not data:
#                     break
#                 yield data

#     return Response(generate(), mimetype='video/mp4')
    # return Response(stream_with_context(generate()), mimetype='video/mp4', 
    #                 headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)}, 
    #                 direct_passthrough=True)


@app.route('/hls/<path:path>')
def serve_hls_file(path):
    return send_from_directory('static/videos', path)


@app.route('/add_video')
def add_sample_video():
    title = "theif" 
    ownership = "umerb"
    genre = "Game"
    release_year = 2023
    bio = "This is sample test video."
    media_type = "mkv"

    new_video = Videos(title=title, ownership=ownership, genre=genre, release_year=release_year, bio=bio, media_type=media_type)
    db.session.add(new_video)
    db.session.commit()

    return 'Sample video added to database!'

@app.route('/getallvideos')
def getallvideos():
    videos = Videos.query.all()
    video_dict = [video.as_dict() for video in videos]
    return json.dumps(video_dict)

def get_all_videos():
    return Videos.query.all()

def get_video_by_id(id):
    return Videos.query.get(id)

def get_videos_by_genre(genre):
    return Videos.query.filter_by(genre=genre).all()

def get_videos_by_release_year(year):
    return Videos.query.filter_by(release_year=year).all()

@app.route('/videos', methods=['GET'])
def all_videos():
    videos = get_all_videos()
    return jsonify([video.as_dict() for video in videos])

@app.route('/videos/<int:id>', methods=['GET'])
def video_by_id(id):
    video = get_video_by_id(id)
    return jsonify(video.as_dict())

@app.route('/thumbnail/<path:path>')
def thumbnail(path):
    return send_from_directory('metapic/title',path)

@app.route('/videos/genre/<string:genre>', methods=['GET'])
def videos_by_genre(genre):
    videos = get_videos_by_genre(genre)
    return jsonify([video.as_dict() for video in videos])

@app.route('/videos/year/<int:year>', methods=['GET'])
def videos_by_year(year):
    videos = get_videos_by_release_year(year)
    return jsonify([video.as_dict() for video in videos])





# def delete_files():
#     now = time.time()
#     for filename, creation_time in list(streamed_files.items()):
#         if now - creation_time > DELETE_TIME:
#             os.remove(os.path.join(STREAM_FOLDER, filename))
#             del streamed_files[filename]

def delete_files():
    now = time.time()
    for folder in STREAM_FOLDER:
        for root, dirs, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                creation_time = os.path.getctime(filepath)
                if now - creation_time > DELETE_TIME:
                    os.remove(filepath)

    timer = threading.Timer(60.0, delete_files)
    timer.start()


@app.route('/<user_id>/<segment>')
# @login_required
def serve_segment(user_id,segment):
    # user=current_user
    id=int(user_id)-secret_cred
    user=User.query.get(id)
    print(user)
    app.logger.info('recieved request for '+str(segment))
    common_path = 'commonsegments\\' + segment
    

    if os.path.exists('commonsegments\\'+segment):
        
        return send_file(common_path)
   
    

    open_path = 'embedded\\' + user.name + '\\' + segment
    if os.path.exists(open_path):
        # streamed_files[segment] = time.time()
        return send_file(open_path)
    
    watermark = Watermark.query.filter_by(user_id=user.id).first()
    if not watermark:
        return 'Watermark not found', 404
    
    watermark_image = Image.open(io.BytesIO(watermark.image_bytes))
    watermark_image = watermark_image.convert('1')  # convert to black and white image
    watermark_image = watermark_image.resize((32, 32))
    watermark_image= np.asarray(watermark_image)

    # logo = cv2.imread("input/5.png")
    # logo = cv2.cvtColor(logo,cv2.COLOR_RGB2GRAY)
    # logo[logo>128] = 255
    # logo[logo <=128] = 0
    # logo = cv2.resize(logo,(64,64))

    path="opensegments\\"+segment

    command = ['ffprobe', '-show_entries', 'format=start_time', '-v', 'quiet', '-of', 'csv=p=0', path]

    output = subprocess.check_output(command)
    start_time = float(output.decode('utf-8').strip().splitlines()[0])
    pathin="input\\"+segment[:-3]+'.mp4'
    
    # print(start_time)
    subprocess.call(['ffmpeg', '-i', path ,'-vcodec', 'copy', '-acodec', 'copy', pathin])
    

    main.embed(watermark_image,segment[:-3]+'.mp4')
    pathout="output\\"+segment[:-3]+'_final.mkv'
    pathhpre="embedded\\"+user.name
    if not os.path.exists(pathhpre):
        os.makedirs(pathhpre)
    pathh=pathhpre+'\\'+segment

    subprocess.call(['ffmpeg', '-i', pathout ,'-vcodec', 'copy', '-acodec', 'copy', pathh])
    # Here
    os.remove(pathout)
    os.remove(pathin)
    #remove pathin,pathout


    # pathhpre="embedded\\"
    # pathh=pathhpre+segment
    # temp=pathhpre+"temp.ts"


    start_time=start_time/2
    # print(start_time)


    
    subprocess.call(['ffmpeg', '-i', pathh, '-map', '0', '-c', 'copy', '-muxpreload', str(start_time) ,'-muxdelay', str(start_time), pathh + '_temp.ts'])
    os.remove(pathh)
    os.rename(pathh + '_temp.ts',pathh)

    # jeez='embedded\\'+segment
    # streamed_files[segment] = time.time()
    return send_file(pathh)





    # If file not found in both folders, return 404 error
    return 'File not found', 404

@app.route('/pirate')
def pirate():
    return render_template('player.html')


@app.route('/match/<creduser>')
def match(creduser):

    id=int(creduser)-secret_cred
    user=User.query.get(id)

    if user.name and user.email:
        return f"Match found! User name: {user.name}, email: {user.email}"
    else:
        return "No match found."


@app.route('/extract')
def ext():
    watermark1 = main.Extract("theif-001.mp4")
    cv2.imwrite("wmtemp/watermark_binary1.jpg", watermark1)
    watermark2 = main.Extract("theif-004.mp4")
    cv2.imwrite("wmtemp/watermark_binary2.jpg", watermark2)
    watermark3 = main.Extract("theif-007.mp4")
    cv2.imwrite("wmtemp/watermark_binary3.jpg", watermark3)
    average_image = np.mean([watermark1, watermark2, watermark3], axis=0)
    Image.fromarray(average_image.astype(np.uint8)).save('wmtemp/watermark_average_image.jpg')
    threshold = 128
    mask = average_image < threshold
    average_image[mask] = 0
    average_image[~mask] = 255


    Image.fromarray(average_image.astype(np.uint8)).save('wmtemp/watermark_best_image.jpg')

    return "Extraction Complete"


@app.route('/')
def hi():
    return "CREDSTREAM"

