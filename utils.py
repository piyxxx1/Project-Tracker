from flask import flash
from datetime import datetime, timedelta

def format_date(date):
    """Format datetime to a readable string."""
    if date is None:
        return None
    return date.strftime('%B %d, %Y, %I:%M %p')

def get_status_color(status):
    """Return Bootstrap color class based on status."""
    status_colors = {
        'Planning': 'info',
        'In Progress': 'primary',
        'Review': 'warning',
        'Completed': 'success',
        'To Do': 'secondary',
        'Done': 'success'
    }
    return status_colors.get(status, 'secondary')

def get_priority_color(priority):
    """Return Bootstrap color class based on priority."""
    priority_colors = {
        'Low': 'info',
        'Medium': 'warning',
        'High': 'danger'
    }
    return priority_colors.get(priority, 'secondary')

def is_deadline_close(deadline):
    """Check if deadline is within 2 days."""
    if deadline is None:
        return False
    return deadline - datetime.utcnow() <= timedelta(days=2)

def flash_errors(form):
    """Flash all errors from a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')

            
