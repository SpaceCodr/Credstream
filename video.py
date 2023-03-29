from app import models
from config import db
from app.models import Videos
from app.views import app

def add_video(title, ownership, genre, release_year, bio=None, media_type="mp4"):
    new_video = Videos(title=title, ownership=ownership, genre=genre, release_year=release_year, bio=bio, media_type=media_type)
    db.session.add(new_video)
    db.session.commit()

def get_all_videos():
    return Videos.query.all()

def get_video_by_id(id):
    return Videos.query.get(id)

def get_videos_by_genre(genre):
    return Videos.query.filter_by(genre=genre).all()

def get_videos_by_release_year(year):
    return Videos.query.filter_by(release_year=year).all()
