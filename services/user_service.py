from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId


def get_db():
    """Get database reference from app module."""
    from flask import current_app
    return current_app.db


def create_user(data):
    """Create a new student user."""
    db = get_db()
    
    user = {
        'name': data['name'].strip(),
        'email': data['email'].strip().lower(),
        'roll_no': data['roll_no'].strip().upper(),
        'department': data['department'],
        'year': data['year'],
        'password_hash': generate_password_hash(data['password']),
        'role': 'student',
        'created_at': datetime.utcnow(),
    }
    
    result = db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user


def authenticate_user(email, password, role='student'):
    """Authenticate a user by email and password."""
    db = get_db()
    
    user = db.users.find_one({
        'email': email.strip().lower(),
        'role': role,
    })
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


def get_user_by_id(user_id):
    """Fetch a user by their ObjectId."""
    db = get_db()
    try:
        return db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None


def get_user_by_email(email):
    """Check if a user exists with this email."""
    db = get_db()
    return db.users.find_one({'email': email.strip().lower()})


def get_user_by_email_and_role(email, role):
    """Find a user by email and role."""
    db = get_db()
    return db.users.find_one({'email': email.strip().lower(), 'role': role})


def get_user_by_roll_no(roll_no):
    """Check if a user exists with this roll number."""
    db = get_db()
    return db.users.find_one({'roll_no': roll_no.strip().upper()})


def update_profile(user_id, data):
    """Update a user's profile fields."""
    db = get_db()
    
    update_fields = {}
    if 'name' in data:
        update_fields['name'] = data['name'].strip()
    if 'department' in data:
        update_fields['department'] = data['department']
    if 'year' in data:
        update_fields['year'] = data['year']
    
    if update_fields:
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_fields}
        )
    
    return get_user_by_id(user_id)


def get_total_students():
    """Get total number of student users."""
    db = get_db()
    return db.users.count_documents({'role': 'student'})


def change_admin_password(user_id, current_password, new_password):
    """Change an admin user's password after verifying the current one.

    Returns a dict with 'success' (bool) and 'message' (str).
    """
    user = get_user_by_id(user_id)
    if not user or user.get('role') != 'admin':
        return {'success': False, 'message': 'Admin user not found.'}

    if not check_password_hash(user['password_hash'], current_password):
        return {'success': False, 'message': 'Current password is incorrect.'}

    if len(new_password) < 6:
        return {'success': False, 'message': 'New password must be at least 6 characters.'}

    db = get_db()
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password_hash': generate_password_hash(new_password)}}
    )

    return {'success': True, 'message': 'Password changed successfully!'}


def change_student_password(user_id, current_password, new_password):
    """Change a student user's password after verifying the current one.

    Returns a dict with 'success' (bool) and 'message' (str).
    """
    user = get_user_by_id(user_id)
    if not user or user.get('role') != 'student':
        return {'success': False, 'message': 'Student user not found.'}

    if not check_password_hash(user['password_hash'], current_password):
        return {'success': False, 'message': 'Current password is incorrect.'}

    if len(new_password) < 6:
        return {'success': False, 'message': 'New password must be at least 6 characters.'}

    db = get_db()
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password_hash': generate_password_hash(new_password)}}
    )

    return {'success': True, 'message': 'Password changed successfully!'}


def create_admin_user(data):
    """Create a new admin user (e.g. teacher)."""
    db = get_db()
    
    admin = {
        'name': data['name'].strip(),
        'email': data['email'].strip().lower(),
        'password_hash': generate_password_hash(data['password']),
        'role': 'admin',
        'is_teacher': data.get('is_teacher', False),
        'created_at': datetime.utcnow(),
    }
    
    result = db.users.insert_one(admin)
    admin['_id'] = result.inserted_id
    return admin


def get_all_admins():
    """Get all users with the admin role."""
    db = get_db()
    return list(db.users.find({'role': 'admin'}))
