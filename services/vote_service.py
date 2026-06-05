from datetime import datetime
from bson import ObjectId


def get_db():
    """Get database reference from app module."""
    from flask import current_app
    return current_app.db


def cast_vote(user_id, election_id, candidate_id):
    """
    Cast a vote. Returns (success, message).
    Enforces ONE STUDENT + ONE ELECTION = ONE VOTE rule.
    """
    db = get_db()
    
    # Check if already voted
    if has_voted(user_id, election_id):
        return False, 'You have already voted in this election.'
    
    # Check election is active
    election = db.elections.find_one({'_id': ObjectId(election_id)})
    if not election or election['status'] != 'active':
        return False, 'This election is not currently active.'
    
    # Check candidate belongs to this election
    candidate = db.candidates.find_one({
        '_id': ObjectId(candidate_id),
        'election_id': str(election_id),
    })
    if not candidate:
        return False, 'Invalid candidate for this election.'
    
    # Record the vote
    vote = {
        'user_id': str(user_id),
        'election_id': str(election_id),
        'candidate_id': str(candidate_id),
        'voted_at': datetime.utcnow(),
    }
    
    try:
        db.votes.insert_one(vote)
        return True, 'Your vote has been securely recorded.'
    except Exception:
        return False, 'An error occurred while recording your vote.'


def has_voted(user_id, election_id):
    """Check if a user has already voted in an election."""
    db = get_db()
    vote = db.votes.find_one({
        'user_id': str(user_id),
        'election_id': str(election_id),
    })
    return vote is not None


def get_results(election_id):
    """
    Aggregate votes per candidate with counts and percentages.
    Returns list of {candidate, votes, percentage}.
    """
    db = get_db()
    
    # Get all candidates for this election
    candidates = list(db.candidates.find({'election_id': str(election_id)}))
    
    # Count total votes for this election
    total_votes = db.votes.count_documents({'election_id': str(election_id)})
    
    results = []
    for candidate in candidates:
        vote_count = db.votes.count_documents({
            'election_id': str(election_id),
            'candidate_id': str(candidate['_id']),
        })
        
        percentage = round((vote_count / total_votes * 100), 1) if total_votes > 0 else 0
        
        results.append({
            'candidate': candidate,
            'votes': vote_count,
            'percentage': percentage,
        })
    
    # Sort by votes descending
    results.sort(key=lambda x: x['votes'], reverse=True)
    
    return {
        'results': results,
        'total_votes': total_votes,
        'winner': results[0] if results and total_votes > 0 else None,
    }


def get_user_voting_history(user_id):
    """
    Get elections a student participated in.
    Does NOT reveal which candidate they voted for (privacy).
    """
    db = get_db()
    
    votes = list(db.votes.find({'user_id': str(user_id)}).sort('voted_at', -1))
    
    history = []
    for vote in votes:
        election = db.elections.find_one({'_id': ObjectId(vote['election_id'])})
        if election:
            history.append({
                'election': election,
                'voted_at': vote.get('voted_at', datetime.utcnow()),
            })
    
    return history


def get_voter_count(election_id):
    """Get total number of unique voters for an election."""
    db = get_db()
    return db.votes.count_documents({'election_id': str(election_id)})


def get_participation_rate(election_id):
    """Calculate participation rate as voters / total students."""
    db = get_db()
    
    total_students = db.users.count_documents({'role': 'student'})
    voter_count = get_voter_count(election_id)
    
    if total_students == 0:
        return 0
    
    return round((voter_count / total_students * 100), 1)


def get_recent_votes(limit=10):
    """Get recent voting activity (for admin dashboard)."""
    db = get_db()
    
    votes = list(db.votes.find().sort('voted_at', -1).limit(limit))
    
    activity = []
    for vote in votes:
        election = db.elections.find_one({'_id': ObjectId(vote['election_id'])})
        if election:
            activity.append({
                'election_title': election['title'],
                'voted_at': vote.get('voted_at', datetime.utcnow()),
            })
    
    return activity
