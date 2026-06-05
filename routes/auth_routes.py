from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.user_service import create_user, authenticate_user, get_user_by_email, get_user_by_roll_no, get_db
from services.email_service import generate_otp, send_otp_email
from config import Config
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/student/send-otp', methods=['POST'])
def send_otp():
    """Generate and send OTP for registration."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email.endswith('@kmclu.ac.in'):
        return jsonify({'success': False, 'message': 'Only @kmclu.ac.in emails are allowed.'}), 400
        
    if get_user_by_email(email):
        return jsonify({'success': False, 'message': 'An account with this email already exists.'}), 400
        
    otp = generate_otp()
    
    db = get_db()
    db.otps.update_one(
        {'email': email},
        {'$set': {'otp': otp, 'createdAt': datetime.utcnow()}},
        upsert=True
    )
    
    if send_otp_email(email, otp):
        return jsonify({'success': True, 'message': 'OTP sent successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'}), 500


@auth_bp.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    """Student registration page."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        roll_no = request.form.get('roll_no', '').strip()
        department = request.form.get('department', '')
        year = request.form.get('year', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        otp_input = request.form.get('otp', '').strip()
        
        # Validation
        errors = []
        if not email.endswith('@kmclu.ac.in'):
            errors.append('Only @kmclu.ac.in emails are allowed.')
        if not all([name, email, roll_no, department, year, password, otp_input]):
            errors.append('All fields are required.')
        
        db = get_db()
        otp_record = db.otps.find_one({'email': email})
        if not otp_record or otp_record.get('otp') != otp_input:
            errors.append('Invalid or expired OTP.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if get_user_by_email(email):
            errors.append('An account with this email already exists.')
        if get_user_by_roll_no(roll_no):
            errors.append('An account with this roll number already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/student_signup.html',
                                   departments=Config.DEPARTMENTS,
                                   years=Config.YEARS,
                                   form_data=request.form)
        
        # Create user
        user = create_user({
            'name': name,
            'email': email,
            'roll_no': roll_no,
            'department': department,
            'year': year,
            'password': password,
        })
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.student_login'))
    
    return render_template('auth/student_signup.html',
                           departments=Config.DEPARTMENTS,
                           years=Config.YEARS)


@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Student login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = authenticate_user(email, password, role='student')
        
        if user:
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_role'] = 'student'
            session['user_department'] = user.get('department', '')
            session['user_year'] = user.get('year', '')
            session['user_email'] = user['email']
            session['user_roll_no'] = user.get('roll_no', '')
            session.permanent = True
            
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('auth/student_login.html', form_data=request.form)
    
    return render_template('auth/student_login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = authenticate_user(email, password, role='admin')
        
        if user:
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_role'] = 'admin'
            session['user_email'] = user['email']
            session.permanent = True
            
            flash('Welcome to the Control Room.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials.', 'error')
            return render_template('auth/admin_login.html', form_data=request.form)
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to landing."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))
