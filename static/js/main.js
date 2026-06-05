/* ═══════════════════════════════════════════════════════
   UNICRACY — Main JavaScript
   Toast notifications, page transitions, utilities
   ═══════════════════════════════════════════════════════ */

/**
 * Show a toast notification.
 * @param {string} message - The message to display
 * @param {string} type - 'success', 'error', 'info', 'warning'
 * @param {number} duration - Auto-dismiss duration in ms (default: 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    // Map flash categories to toast types
    const typeMap = {
        'success': 'success',
        'error': 'error',
        'danger': 'error',
        'info': 'info',
        'warning': 'warning',
    };
    type = typeMap[type] || 'info';
    
    const icons = {
        success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        info: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
        warning: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        ${icons[type] || icons.info}
        <span>${message}</span>
        <button class="toast-close" onclick="dismissToast(this.parentElement)">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto dismiss
    setTimeout(() => {
        dismissToast(toast);
    }, duration);
}

/**
 * Dismiss a toast with exit animation.
 */
function dismissToast(toast) {
    if (!toast || toast.classList.contains('toast-exit')) return;
    toast.classList.add('toast-exit');
    setTimeout(() => {
        if (toast.parentElement) {
            toast.parentElement.removeChild(toast);
        }
    }, 300);
}

/**
 * Initialize page transitions - fade in on load.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Page content is already animated via CSS class .page-content
    // This ensures any dynamically added content also gets the treatment
    
    // Initialize floating labels for pre-filled inputs
    document.querySelectorAll('.form-input').forEach(input => {
        if (input.value && input.value.trim() !== '') {
            const label = input.nextElementSibling;
            if (label && label.classList.contains('form-label')) {
                // CSS handles this via :not(:placeholder-shown)
            }
        }
    });
});
