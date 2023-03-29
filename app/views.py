from datetime import datetime
from flask import request, jsonify, make_response,Response,stream_with_context,send_from_directory
from flask_login import (
    login_user,
    current_user,
    logout_user,
    login_required
)
from werkzeug.security import check_password_hash, generate_password_hash
from app import models
from config import db, bcrypt, login_manager, create_app
from app.models import User,Videos
import os
import cv2
import numpy as np
import json

app = create_app()
secret_cred=1257

@app.route('/api/test')
def test_api():
    return jsonify({'message': 'Hello, Flutter!'})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(name=data['name'], date_of_birth=data['date_of_birth'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'message': 'User created successfully!'}),201)

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
    title = "hope" 
    ownership = "umerb"
    genre = "Test"
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
    video_dicts = [video.as_dict() for video in videos]
    return json.dumps(video_dicts)

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

@app.route('/videos/genre/<string:genre>', methods=['GET'])
def videos_by_genre(genre):
    videos = get_videos_by_genre(genre)
    return jsonify([video.as_dict() for video in videos])

@app.route('/videos/year/<int:year>', methods=['GET'])
def videos_by_year(year):
    videos = get_videos_by_release_year(year)
    return jsonify([video.as_dict() for video in videos])

@app.route('/thumbnail/<path:path>')
def thumbnail(path):
    return send_from_directory('metapic/title',path)