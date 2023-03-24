from datetime import datetime
from flask import request, jsonify, make_response
from flask_login import (
    login_user,
    current_user,
    logout_user,
    login_required
)
from werkzeug.security import check_password_hash, generate_password_hash
from app import models
from config import db, bcrypt, login_manager, create_app
from app.models import User

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
