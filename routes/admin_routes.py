from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from services.election_service import (
    create_election, get_all_elections, get_election_by_id,
    get_candidates, add_candidate, delete_candidate,
    activate_election, close_election, get_election_stats
)
from services.vote_service import (
    get_results, get_voter_count, get_participation_rate, get_recent_votes
)
from services.user_service import get_total_students
from config import Config

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    """Admin dashboard — the Election Control Room."""
    stats = get_election_stats()
    recent_activity = get_recent_votes(limit=10)
    elections = get_all_elections()
    total_students = get_total_students()
    
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_activity=recent_activity,
                           elections=elections,
                           total_students=total_students)


@admin_bp.route('/admin/elections')
@admin_required
def elections():
    """All elections management list."""
    all_elections = get_all_elections()
    
    for election in all_elections:
        election['candidate_count'] = len(get_candidates(str(election['_id'])))
        election['voter_count'] = get_voter_count(str(election['_id']))
    
    return render_template('admin/elections.html', elections=all_elections)


@admin_bp.route('/admin/election/create', methods=['GET', 'POST'])
@admin_required
def create_election_route():
    """Create a new election."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        post_name = request.form.get('post_name', '').strip()
        description = request.form.get('description', '').strip()
        department = request.form.get('department', 'All Departments')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        
        if not title or not post_name:
            flash('Title and Post Name are required.', 'error')
            return render_template('admin/create_election.html',
                                   departments=Config.DEPARTMENTS,
                                   form_data=request.form)
        
        election = create_election({
            'title': title,
            'post_name': post_name,
            'description': description,
            'department': department,
            'start_date': start_date,
            'end_date': end_date,
            'created_by': session['user_id'],
        })
        
        flash('Election created successfully!', 'success')
        return redirect(url_for('admin.elections'))
    
    return render_template('admin/create_election.html',
                           departments=Config.DEPARTMENTS)


@admin_bp.route('/admin/election/<election_id>/candidates', methods=['GET', 'POST'])
@admin_required
def manage_candidates(election_id):
    """View and add candidates to an election."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('admin.elections'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        department = request.form.get('department', '')
        year = request.form.get('year', '')
        manifesto = request.form.get('manifesto', '').strip()
        symbol = request.form.get('symbol', '🗳️').strip()
        
        if not name:
            flash('Candidate name is required.', 'error')
        else:
            add_candidate(election_id, {
                'name': name,
                'roll_no': roll_no,
                'department': department,
                'year': year,
                'manifesto': manifesto,
                'symbol': symbol,
            })
            flash(f'Candidate "{name}" added successfully!', 'success')
        
        return redirect(url_for('admin.manage_candidates', election_id=election_id))
    
    candidates = get_candidates(election_id)
    
    return render_template('admin/candidates.html',
                           election=election,
                           candidates=candidates,
                           departments=Config.DEPARTMENTS,
                           years=Config.YEARS)


@admin_bp.route('/admin/election/<election_id>/results')
@admin_required
def election_results(election_id):
    """View election results (admin view with extra stats)."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('admin.elections'))
    
    result_data = get_results(election_id)
    voter_count = get_voter_count(election_id)
    participation = get_participation_rate(election_id)
    total_students = get_total_students()
    
    return render_template('admin/results.html',
                           election=election,
                           results=result_data['results'],
                           winner=result_data['winner'],
                           total_votes=result_data['total_votes'],
                           voter_count=voter_count,
                           participation_rate=participation,
                           total_students=total_students)


@admin_bp.route('/admin/election/<election_id>/activate', methods=['POST'])
@admin_required
def activate_election_route(election_id):
    """Activate an election."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('admin.elections'))
    
    if election['status'] != 'upcoming':
        flash('Only upcoming elections can be activated.', 'error')
    else:
        candidates = get_candidates(election_id)
        if len(candidates) < 2:
            flash('An election needs at least 2 candidates to be activated.', 'error')
        else:
            activate_election(election_id)
            flash(f'Election "{election["title"]}" is now ACTIVE!', 'success')
    
    return redirect(url_for('admin.elections'))


@admin_bp.route('/admin/election/<election_id>/close', methods=['POST'])
@admin_required
def close_election_route(election_id):
    """Close an election."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('admin.elections'))
    
    if election['status'] != 'active':
        flash('Only active elections can be closed.', 'error')
    else:
        close_election(election_id)
        flash(f'Election "{election["title"]}" has been CLOSED.', 'success')
    
    return redirect(url_for('admin.elections'))


@admin_bp.route('/admin/election/<election_id>/candidate/<candidate_id>/delete', methods=['POST'])
@admin_required
def delete_candidate_route(election_id, candidate_id):
    """Delete a candidate from an election."""
    election = get_election_by_id(election_id)
    if not election:
        flash('Election not found.', 'error')
        return redirect(url_for('admin.elections'))
    
    if election['status'] != 'upcoming':
        flash('Cannot modify candidates of an active or closed election.', 'error')
    else:
        delete_candidate(candidate_id)
        flash('Candidate removed.', 'success')
    
    return redirect(url_for('admin.manage_candidates', election_id=election_id))
