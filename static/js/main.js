// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Task status update
    const statusSelects = document.querySelectorAll('.task-status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const taskId = this.getAttribute('data-task-id');
            const newStatus = this.value;

            // Change the badge color based on new status
            const statusBadge = document.querySelector(`#task-${taskId}-badge`);
            if (statusBadge) {
                statusBadge.className = `badge bg-${getStatusColor(newStatus)}`;
                statusBadge.textContent = newStatus;
            }

            // You could send this update to the server via fetch API
            // For now, just show visual feedback
            const toastContainer = document.getElementById('toast-container');
            if (toastContainer) {
                const toast = document.createElement('div');
                toast.className = 'toast align-items-center text-white bg-success border-0';
                toast.setAttribute('role', 'alert');
                toast.setAttribute('aria-live', 'assertive');
                toast.setAttribute('aria-atomic', 'true');
                
                toast.innerHTML = `
                    <div class="d-flex">
                        <div class="toast-body">
                            Task status updated to ${newStatus}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                `;
                
                toastContainer.appendChild(toast);
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
                
                // Remove toast after it's hidden
                toast.addEventListener('hidden.bs.toast', function() {
                    toast.remove();
                });
            }
        });
    });

    // Deadline warnings
    const deadlineElements = document.querySelectorAll('.deadline-text');
    deadlineElements.forEach(element => {
        const deadlineDate = new Date(element.getAttribute('data-deadline'));
        const now = new Date();
        const diffTime = deadlineDate - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays < 0) {
            element.classList.add('text-danger', 'fw-bold');
            element.innerHTML += ' <span class="badge bg-danger">Overdue!</span>';
        } else if (diffDays <= 2) {
            element.classList.add('text-warning', 'fw-bold');
            element.innerHTML += ' <span class="badge bg-warning text-dark">Soon!</span>';
        }
    });

    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});

// Helper function to get status color
function getStatusColor(status) {
    const statusColors = {
        'Planning': 'info',
        'In Progress': 'primary',
        'Review': 'warning',
        'Completed': 'success',
        'To Do': 'secondary',
        'Done': 'success'
    };
    return statusColors[status] || 'secondary';
}

// Helper function to get priority color
function getPriorityColor(priority) {
    const priorityColors = {
        'Low': 'info',
        'Medium': 'warning',
        'High': 'danger'
    };
    return priorityColors[priority] || 'secondary';
}

// Project progress chart initialization (if exists on page)
if (document.getElementById('projectProgressChart')) {
    const ctx = document.getElementById('projectProgressChart').getContext('2d');
    const projectProgressChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Remaining'],
            datasets: [{
                data: [
                    parseInt(document.getElementById('projectProgressChart').getAttribute('data-completed')),
                    parseInt(document.getElementById('projectProgressChart').getAttribute('data-remaining'))
                ],
                backgroundColor: [
                    'rgb(40, 167, 69)',  // green for completed
                    'rgb(108, 117, 125)' // gray for remaining
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'white'
                    }
                }
            }
        }
    });
}
