/* ═══════════════════════════════════════════════════════
   UNICRACY — Vote Page JavaScript
   Confirmation modal, vote casting, receipt display
   ═══════════════════════════════════════════════════════ */

let selectedCandidateId = null;
let selectedCandidateName = null;

/**
 * Open the vote confirmation modal.
 */
function openConfirmModal(candidateId, candidateName) {
    selectedCandidateId = candidateId;
    selectedCandidateName = candidateName;
    
    document.getElementById('modal-candidate-name').textContent = candidateName;
    document.getElementById('vote-modal').classList.add('active');
}

/**
 * Close the vote confirmation modal.
 */
function closeConfirmModal() {
    document.getElementById('vote-modal').classList.remove('active');
    selectedCandidateId = null;
    selectedCandidateName = null;
}

/**
 * Cast the vote via AJAX.
 */
function castVote() {
    if (!selectedCandidateId) return;
    
    const btn = document.getElementById('confirm-vote-btn');
    const spinner = document.getElementById('vote-spinner');
    
    // Show loading state
    btn.classList.add('btn-loading');
    spinner.classList.remove('hidden');
    
    fetch(`/student/vote/${electionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            candidate_id: selectedCandidateId,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            closeConfirmModal();
            
            // Show receipt
            showReceipt();
            
            // Lock all vote buttons
            lockAllButtons();
            
        } else {
            // Show error
            closeConfirmModal();
            showToast(data.message || 'Failed to cast vote.', 'error');
        }
    })
    .catch(error => {
        closeConfirmModal();
        showToast('An error occurred. Please try again.', 'error');
        console.error('Vote error:', error);
    })
    .finally(() => {
        btn.classList.remove('btn-loading');
        spinner.classList.add('hidden');
    });
}

/**
 * Show the vote receipt overlay.
 */
function showReceipt() {
    const now = new Date();
    const timestamp = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
    
    document.getElementById('receipt-timestamp').textContent = timestamp;
    document.getElementById('vote-receipt').classList.add('active');
}

/**
 * Lock all vote buttons after casting a vote.
 */
function lockAllButtons() {
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.disabled = true;
        btn.className = 'btn btn-locked btn-block';
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Vote Locked
        `;
    });
}

/**
 * Toggle manifesto text expansion.
 */
function toggleManifesto(candidateId, fullText) {
    const el = document.getElementById('manifesto-' + candidateId);
    const btn = el.nextElementSibling;
    
    if (btn.textContent === 'Read More') {
        el.textContent = fullText;
        btn.textContent = 'Show Less';
    } else {
        el.textContent = fullText.substring(0, 150) + '...';
        btn.textContent = 'Read More';
    }
}

// Close modal on overlay click
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('vote-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeConfirmModal();
            }
        });
    }
    
    // Close receipt on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeConfirmModal();
        }
    });
});

// Sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('mobile-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (toggle && sidebar && overlay) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }
});
