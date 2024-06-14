from flask import Flask, session, request, jsonify, current_app
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
from flask_cors import CORS
from flask_mail import Mail
from .models import Profile
from authlib.integrations.flask_client import OAuth
import os
from flask_sock import Sock
import firebase_admin
from firebase_admin import credentials, initialize_app
from firebase_admin.exceptions import FirebaseError
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
jwt = JWTManager()
oauth = OAuth()
csrf = CSRFProtect()
sock = Sock()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    CORS(app)
    mail.init_app(app)
    sock.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        oauth.init_app(app)
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
            client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_params=None,
            refresh_token_url=None,
            client_kwargs={'scope': 'openid profile email'},
        )

    cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    print(f"Using Firebase credential path: {cred_path}")
    if cred_path and os.path.exists(cred_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                initialize_app(cred)
                print("Firebase initialized successfully")
        except FirebaseError as e:
            print(f"Firebase initialization error: {e}")
    else:
        print(f"Firebase credential path {cred_path} is invalid or does not exist.")

    @login.user_loader
    def load_user(user_id):
        return Profile.query.get(user_id)

    from .api.auth_routes import auth_routes
    from .api.profile_routes import profile_routes
    from .api.channel_routes import channel_routes

    app.register_blueprint(auth_routes, url_prefix='/api/auth')
    app.register_blueprint(profile_routes, url_prefix='/api/profiles')
    app.register_blueprint(channel_routes, url_prefix='/api/channels')

    @app.route('/')
    def index():
        return "Hello, World!"

    @app.after_request
    def inject_csrf_token(response):
        csrf_token = session.get('csrf_token', generate_csrf())
        session['csrf_token'] = csrf_token
        response.set_cookie(
            'csrf_token',
            csrf_token,
            secure=True,
            samesite='Strict',
            httponly=True
        )
        return response

    @app.before_request
    def log_session_info():
        session.permanent = True
        csrf_token = session.get('csrf_token', generate_csrf())
        session['csrf_token'] = csrf_token

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({'error': 'CSRF token missing or incorrect'}), 400

    csrf.exempt(auth_routes)
    csrf.exempt(profile_routes)
    csrf.exempt(channel_routes)

    return app, sock
