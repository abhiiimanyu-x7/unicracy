import os
import click
from flask import Flask, render_template, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from authlib.integrations.flask_client import OAuth
from config import Config
from datetime import datetime


# ── MongoDB Client (module-level for service imports) ──
db = None

# ── OAuth Client (module-level for route imports) ──
oauth = OAuth()


def create_app():
    """Application factory."""
    global db
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ── MongoDB Connection ──
    client = MongoClient(app.config['MONGODB_URI'])
    db_name = app.config['MONGODB_URI'].split('/')[-1].split('?')[0] or 'unicracy'
    db = client[db_name]
    
    # Store db on app for access in routes
    app.db = db
    
    # ── OAuth Setup ──
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        },
    )
    # Store oauth on app for access in routes
    app.oauth = oauth
    
    # ── Ensure indexes (tolerant of existing indexes) ──
    try:
        db.users.create_index('email', unique=True)
    except Exception:
        pass
    try:
        db.users.create_index('roll_no', unique=True, sparse=True)
    except Exception:
        pass
    try:
        db.votes.create_index([('user_id', 1), ('election_id', 1)], unique=True)
    except Exception:
        pass
    try:
        db.otps.create_index('createdAt', expireAfterSeconds=app.config['OTP_EXPIRY_SECONDS'])
    except Exception:
        pass
    
    # ── Register Blueprints ──
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    
    # ── Landing Route ──
    @app.route('/')
    def landing():
        if 'user_id' in session:
            if session.get('user_role') == 'admin':
                return render_template('landing.html', logged_in=True, role='admin')
            return render_template('landing.html', logged_in=True, role='student')
        return render_template('landing.html', logged_in=False)
    
    # ── Context Processor ──
    @app.context_processor
    def inject_globals():
        return {
            'departments': Config.DEPARTMENTS,
            'years': Config.YEARS,
            'current_year': datetime.now().year,
            'google_login_enabled': bool(Config.GOOGLE_CLIENT_ID),
        }
    
    # ── Error Handlers ──
    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', error=404, error_message='Page not found'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', error=500, error_message='Internal server error'), 500
    
    existing = db.users.find_one({'email': 'admin@unicracy.com'})

    if not existing:
        admin = {
        'name': 'Admin',
        'email': 'admin@unicracy.com',
        'roll_no': None,
        'department': 'Administration',
        'year': None,
        'password_hash': generate_password_hash('admin123123'),
        'role': 'admin',
        'created_at': datetime.utcnow(),
    }
    db.users.insert_one(admin)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, port=5000)
