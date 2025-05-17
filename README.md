# Project Tracker -  Project Management System

A comprehensive Flask-based web application designed to help students  manage their  projects efficiently.

## Features

- **User Authentication**: Secure registration and login system
- **Project Management**: Create, edit, and delete projects with deadlines and status tracking
- **Task Tracking**: Break down projects into manageable tasks with priorities
- **Progress Monitoring**: Visual representation of project completion status
- **Notes System**: Add important notes to projects for reference
- **Responsive Design**: Mobile-friendly dark theme using Bootstrap

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-Login for user session management
- **Forms**: Flask-WTF for form handling and validation
- **Frontend**: Bootstrap 5, Font Awesome, Chart.js
- **Deployment**: Gunicorn WSGI HTTP Server

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/piyxxx1/project-tracker.git
   cd project-tracker
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```
   export FLASK_APP=main.py
   export DATABASE_URL=mysql+pymysql://root:root@localhost/projecttracker
   export SESSION_SECRET=your-secret-key
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```
   or for production:
   ```
   gunicorn main:app
   ```

## Project Structure

- `app.py`: Application configuration
- `main.py`: Entry point to run the application
- `models.py`: Database models using SQLAlchemy
- `forms.py`: Form classes using Flask-WTF
- `routes.py`: Route handlers and business logic
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static assets

## Future Enhancements

- Team collaboration features
- File upload for project documents
- Calendar integration
- Data visualization for better insights
- Export functionality for reports

## License

This project is licensed under the MIT License - see the LICENSE file for details.
