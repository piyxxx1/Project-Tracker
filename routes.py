from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Project, Task, Note
from forms import LoginForm, RegistrationForm, ProjectForm, TaskForm, NoteForm
from urllib.parse import urlparse
from datetime import datetime
import logging

@app.route('/')
def index():
    """Home page route."""
    if current_user.is_authenticated:
        ongoing_projects = Project.query.filter_by(user_id=current_user.id)\
            .filter(Project.status != 'Completed')\
            .order_by(Project.deadline).limit(5).all()
        upcoming_tasks = Task.query.filter_by(user_id=current_user.id)\
            .filter(Task.status != 'Done')\
            .order_by(Task.deadline).limit(5).all()
        return render_template('index.html', ongoing_projects=ongoing_projects, upcoming_tasks=upcoming_tasks)
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        flash('You have been logged in!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error registering user: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    projects_count = Project.query.filter_by(user_id=current_user.id).count()
    completed_projects = Project.query.filter_by(user_id=current_user.id, status='Completed').count()
    tasks_count = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status='Done').count()
    
    return render_template('profile.html', 
                          projects_count=projects_count,
                          completed_projects=completed_projects,
                          tasks_count=tasks_count,
                          completed_tasks=completed_tasks)


@app.route('/projects')
@login_required
def projects():
    """List all projects of the current user."""
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)


@app.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project."""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            status=form.status.data,
            user_id=current_user.id
        )
        db.session.add(project)
        try:
            db.session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating project: {e}")
            flash('An error occurred while creating the project.', 'danger')
    
    return render_template('create_project.html', form=form, title='Create Project')


@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Show details of a specific project."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.deadline).all()
    notes = Note.query.filter_by(project_id=project_id).order_by(Note.created_at.desc()).all()
    
    # Task statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'Done')
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    note_form = NoteForm()
    
    return render_template('project_detail.html', 
                          project=project, 
                          tasks=tasks, 
                          notes=notes,
                          note_form=note_form,
                          total_tasks=total_tasks,
                          completed_tasks=completed_tasks,
                          completion_percentage=completion_percentage)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit an existing project."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.deadline = form.deadline.data
        project.status = form.status.data
        project.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating project: {e}")
            flash('An error occurred while updating the project.', 'danger')
    
    return render_template('create_project.html', form=form, title='Edit Project')


@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete a project."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting project: {e}")
        flash('An error occurred while deleting the project.', 'danger')
    
    return redirect(url_for('projects'))


@app.route('/projects/<int:project_id>/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    """Create a new task for a project."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            status=form.status.data,
            priority=form.priority.data,
            project_id=project_id,
            user_id=current_user.id
        )
        db.session.add(task)
        try:
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating task: {e}")
            flash('An error occurred while creating the task.', 'danger')
    
    return render_template('create_task.html', form=form, project=project)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=task.project_id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating task: {e}")
            flash('An error occurred while updating the task.', 'danger')
    
    return render_template('create_task.html', form=form, project=task.project, edit_mode=True)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    project_id = task.project_id
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting task: {e}")
        flash('An error occurred while deleting the task.', 'danger')
    
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/projects/<int:project_id>/notes/add', methods=['POST'])
@login_required
def add_note(project_id):
    """Add a note to a project."""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            content=form.content.data,
            project_id=project_id
        )
        db.session.add(note)
        try:
            db.session.commit()
            flash('Note added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding note: {e}")
            flash('An error occurred while adding the note.', 'danger')
    
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a note."""
    note = Note.query.get_or_404(note_id)
    project = Project.query.get_or_404(note.project_id)
    if project.user_id != current_user.id:
        abort(403)
    
    project_id = note.project_id
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting note: {e}")
        flash('An error occurred while deleting the note.', 'danger')
    
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/tasks')
@login_required
def tasks():
    """List all tasks of the current user."""
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline).all()
    return render_template('tasks.html', tasks=tasks)


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, message='Page not found'), 404


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors."""
    return render_template('error.html', error_code=403, message='Forbidden'), 403


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('error.html', error_code=500, message='Internal server error'), 500
