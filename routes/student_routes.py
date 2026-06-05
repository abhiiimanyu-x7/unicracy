from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from services.election_service import (
    get_all_elections, get_election_by_id, get_candidates,
    get_elections_by_status
)
from services.vote_service import (
    cast_vote, has_voted, get_results, get_user_voting_history,
    get_voter_count, get_participation_rate
)
from services.user_service import get_user_by_id, update_profile
from config import Config

student_bp = Blueprint('student', __name__)


def student_required(f):
    """Decorator to require student login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'student':
            flash('Please log in as a student to access this page.', 'error')
            return redirect(url_for('auth.student_login'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/student/dashboard')
@student_required
def dashboard():
    """Student dashboard with election overview."""
    active = get_elections_by_status('active')
    upcoming = get_elections_by_status('upcoming')
    closed = get_elections_by_status('closed')
    
    # Check vote status for each active election
    for election in active:
        election['has_voted'] = has_voted(session['user_id'], str(election['_id']))
    
    for election in closed:
        election['has_voted'] = has_voted(session['user_id'], str(election['_id']))
    
    return render_template('student/dashboard.html',
                           active_elections=active,
                           upcoming_elections=upcoming,
                           closed_elections=closed)


@student_bp.route('/student/elections')
@student_required
def elections():
    """All elections listing."""
    all_elections = get_all_elections()
    
    for election in all_elections:
        election['has_voted'] = has_voted(session['user_id'], str(election['_id']))
        election['candidate_count'] = len(get_candidates(str(election['_id'])))
        election['voter_count'] = get_voter_count(str(election['_id']))
    
    return render_template('student/elections.html', elections=all_elections)


@student_bp.route('/student/vote/<election_id>', methods=['GET'])
@student_required
def vote_page(election_id):
    """Vote page for a specific election."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('student.elections'))
    
    candidates = get_candidates(election_id)
    voted = has_voted(session['user_id'], election_id)
    
    return render_template('student/vote.html',
                           election=election,
                           candidates=candidates,
                           has_voted=voted)


@student_bp.route('/student/vote/<election_id>', methods=['POST'])
@student_required
def cast_vote_route(election_id):
    """Cast a vote (AJAX endpoint)."""
    candidate_id = request.json.get('candidate_id') if request.is_json else request.form.get('candidate_id')
    
    if not candidate_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'No candidate selected.'}), 400
        flash('No candidate selected.', 'error')
        return redirect(url_for('student.vote_page', election_id=election_id))
    
    success, message = cast_vote(session['user_id'], election_id, candidate_id)
    
    if request.is_json:
        status_code = 200 if success else 400
        return jsonify({'success': success, 'message': message}), status_code
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('student.vote_page', election_id=election_id))


@student_bp.route('/student/results/<election_id>')
@student_required
def results(election_id):
    """View election results."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('student.elections'))
    
    result_data = get_results(election_id)
    voter_count = get_voter_count(election_id)
    participation = get_participation_rate(election_id)
    
    return render_template('student/results.html',
                           election=election,
                           results=result_data['results'],
                           winner=result_data['winner'],
                           total_votes=result_data['total_votes'],
                           voter_count=voter_count,
                           participation_rate=participation)


@student_bp.route('/student/profile', methods=['GET', 'POST'])
@student_required
def profile():
    """Student profile page."""
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '')
        year = request.form.get('year', '')
        
        if name:
            updated_user = update_profile(session['user_id'], {
                'name': name,
                'department': department,
                'year': year,
            })
            session['user_name'] = updated_user['name']
            session['user_department'] = updated_user.get('department', '')
            session['user_year'] = updated_user.get('year', '')
            flash('Profile updated successfully.', 'success')
        else:
            flash('Name is required.', 'error')
        
        return redirect(url_for('student.profile'))
    
    voting_history = get_user_voting_history(session['user_id'])
    
    return render_template('student/profile.html',
                           user=user,
                           voting_history=voting_history,
                           departments=Config.DEPARTMENTS,
                           years=Config.YEARS)
