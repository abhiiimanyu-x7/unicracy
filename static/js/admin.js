/* ═══════════════════════════════════════════════════════
   UNICRACY — Admin JavaScript
   View switcher, filter tabs, form helpers
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function() {
    // ── View Switcher (Grid ↔ Table) ──
    const gridBtn = document.getElementById('grid-view-btn');
    const tableBtn = document.getElementById('table-view-btn');
    const gridView = document.getElementById('grid-view');
    const tableView = document.getElementById('table-view');
    
    if (gridBtn && tableBtn && gridView && tableView) {
        gridBtn.addEventListener('click', function() {
            gridBtn.classList.add('active');
            tableBtn.classList.remove('active');
            gridView.classList.remove('hidden');
            tableView.classList.add('hidden');
        });
        
        tableBtn.addEventListener('click', function() {
            tableBtn.classList.add('active');
            gridBtn.classList.remove('active');
            tableView.classList.remove('hidden');
            gridView.classList.add('hidden');
        });
    }
    
    // ── Filter Tabs ──
    const tabs = document.querySelectorAll('.filter-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            
            // Filter grid view cards
            if (gridView) {
                gridView.querySelectorAll('.election-card').forEach(card => {
                    if (filter === 'all' || card.dataset.status === filter) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
            
            // Filter table view rows
            if (tableView) {
                tableView.querySelectorAll('tbody tr').forEach(row => {
                    if (filter === 'all' || row.dataset.status === filter) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });
});
