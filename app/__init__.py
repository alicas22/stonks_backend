import os
from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_cors import CORS
from flask_mail import Mail
from flask_socketio import SocketIO, join_room, leave_room, emit, send
import firebase_admin
from firebase_admin import credentials, initialize_app
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
mail = Mail()
socketio = SocketIO()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    CORS(app)
    mail.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)

    cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    print(f"Using Firebase credential path: {cred_path}")
    if cred_path and os.path.exists(cred_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                initialize_app(cred)
                print("Firebase initialized successfully")
        except firebase_admin.exceptions.FirebaseError as e:
            print(f"Firebase initialization error: {e}")
    else:
        print(f"Firebase credential path {cred_path} is invalid or does not exist.")

    @login.user_loader
    def load_user(user_id):
        return Profile.query.get(user_id)

    @app.route('/')
    def index():
        return "Hello, World!"

    @app.before_request
    def https_redirect():
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, 301)

    @app.after_request
    def inject_csrf_token(response):
        response.set_cookie(
            'csrf_token',
            generate_csrf(),
            secure=True,
            samesite='Strict',
            httponly=True
        )
        return response

    @app.route('/csrf-token', methods=['GET'])
    def get_csrf_token():
        token = generate_csrf()
        response = jsonify({"csrf_token": token})
        response.set_cookie('csrf_token', token, secure=True, samesite='Strict', httponly=True)
        return response

    return app, socketio



if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, debug=True)
