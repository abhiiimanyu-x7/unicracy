import os
import click
from flask import Flask, render_template, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from authlib.integrations.flask_client import OAuth
from config import Config
from datetime import datetime


db = None
oauth = OAuth()


def create_app():
    global db

    app = Flask(__name__)
    app.config.from_object(Config)

    client = MongoClient(app.config['MONGODB_URI'])
    db_name = app.config['MONGODB_URI'].split('/')[-1].split('?')[0] or 'unicracy'
    db = client[db_name]
    app.db = db

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
    app.oauth = oauth

    try:
        db.users.create_index('email', unique=True)
        db.users.create_index('roll_no', unique=True, sparse=True)
        db.votes.create_index([('user_id', 1), ('election_id', 1)], unique=True)
        db.otps.create_index('createdAt', expireAfterSeconds=app.config['OTP_EXPIRY_SECONDS'])
    except Exception:
        pass

    # Auto seed default admin only once
    existing_admin = db.users.find_one({'email': 'admin@unicracy.com'})

    if not existing_admin:
        default_admin = {
            'name': 'Admin',
            'email': 'admin@unicracy.com',
            'roll_no': None,
            'department': 'Administration',
            'year': None,
            'password_hash': generate_password_hash('admin123123'),
            'role': 'admin',
            'created_at': datetime.utcnow(),
        }
        db.users.insert_one(default_admin)

    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def landing():
        if 'user_id' in session:
            if session.get('user_role') == 'admin':
                return render_template('landing.html', logged_in=True, role='admin')
            return render_template('landing.html', logged_in=True, role='student')
        return render_template('landing.html', logged_in=False)

    @app.context_processor
    def inject_globals():
        return {
            'departments': Config.DEPARTMENTS,
            'years': Config.YEARS,
            'current_year': datetime.now().year,
            'google_login_enabled': bool(Config.GOOGLE_CLIENT_ID),
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', error=404, error_message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', error=500, error_message='Internal server error'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, port=5000)