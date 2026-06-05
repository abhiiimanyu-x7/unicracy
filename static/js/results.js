/* ═══════════════════════════════════════════════════════
   UNICRACY — Results Page JavaScript
   Progress bar animations using Intersection Observer
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function() {
    // Animate progress bars when they come into view
    const progressBars = document.querySelectorAll('.progress-bar[data-percentage]');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const percentage = bar.dataset.percentage || 0;
                    
                    // Slight delay for visual effect
                    setTimeout(() => {
                        bar.style.width = percentage + '%';
                    }, 200);
                    
                    observer.unobserve(bar);
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px',
        });
        
        progressBars.forEach(bar => {
            observer.observe(bar);
        });
    } else {
        // Fallback: animate all bars immediately
        setTimeout(() => {
            progressBars.forEach(bar => {
                const percentage = bar.dataset.percentage || 0;
                bar.style.width = percentage + '%';
            });
        }, 300);
    }
});
