from datetime import datetime
from bson import ObjectId


def get_db():
    """Get database reference from app module."""
    from flask import current_app
    return current_app.db


def create_election(data):
    """Create a new election."""
    db = get_db()
    
    election = {
        'title': data['title'].strip(),
        'post_name': data['post_name'].strip(),
        'description': data.get('description', '').strip(),
        'department': data.get('department', 'All Departments'),
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'status': 'upcoming',
        'created_at': datetime.utcnow(),
        'created_by': data.get('created_by'),
    }
    
    result = db.elections.insert_one(election)
    election['_id'] = result.inserted_id
    return election


def get_all_elections():
    """Return all elections, sorted by created_at descending."""
    db = get_db()
    return list(db.elections.find().sort('created_at', -1))


def get_election_by_id(election_id):
    """Get a single election by its ObjectId."""
    db = get_db()
    try:
        return db.elections.find_one({'_id': ObjectId(election_id)})
    except Exception:
        return None


def get_elections_by_status(status):
    """Filter elections by status (upcoming, active, closed)."""
    db = get_db()
    return list(db.elections.find({'status': status}).sort('created_at', -1))


def activate_election(election_id):
    """Set an election's status to active."""
    db = get_db()
    db.elections.update_one(
        {'_id': ObjectId(election_id)},
        {'$set': {'status': 'active'}}
    )


def close_election(election_id):
    """Set an election's status to closed."""
    db = get_db()
    db.elections.update_one(
        {'_id': ObjectId(election_id)},
        {'$set': {'status': 'closed'}}
    )


def get_candidates(election_id):
    """Fetch all candidates for a given election."""
    db = get_db()
    return list(db.candidates.find({'election_id': str(election_id)}).sort('created_at', 1))


def add_candidate(election_id, data):
    """Add a candidate to an election."""
    db = get_db()
    
    candidate = {
        'election_id': str(election_id),
        'name': data['name'].strip(),
        'roll_no': data.get('roll_no', '').strip().upper(),
        'department': data.get('department', ''),
        'year': data.get('year', ''),
        'manifesto': data.get('manifesto', '').strip(),
        'symbol': data.get('symbol', '🗳️'),
        'photo_url': data.get('photo_url', ''),
        'created_at': datetime.utcnow(),
    }
    
    result = db.candidates.insert_one(candidate)
    candidate['_id'] = result.inserted_id
    return candidate


def delete_candidate(candidate_id):
    """Delete a candidate by ID."""
    db = get_db()
    try:
        db.candidates.delete_one({'_id': ObjectId(candidate_id)})
    except Exception:
        pass


def get_election_stats():
    """Get aggregate stats for admin dashboard."""
    db = get_db()
    
    total_elections = db.elections.count_documents({})
    active_elections = db.elections.count_documents({'status': 'active'})
    upcoming_elections = db.elections.count_documents({'status': 'upcoming'})
    closed_elections = db.elections.count_documents({'status': 'closed'})
    total_candidates = db.candidates.count_documents({})
    total_votes = db.votes.count_documents({})
    
    return {
        'total_elections': total_elections,
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'closed_elections': closed_elections,
        'total_candidates': total_candidates,
        'total_votes': total_votes,
    }
