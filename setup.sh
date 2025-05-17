#!/bin/bash

# Project Tracker Setup Script (MySQL version)

echo "Setting up Project Tracker application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv project
source project/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "MySQL is not detected. Please make sure MySQL is installed and running."
    echo "You will need to set up the database manually."
else
    echo "MySQL detected."
    read -p "Would you like to create a new MySQL database for the project? (y/n): " create_db

    if [ "$create_db" = "y" ]; then
        read -p "Enter database name (default: projecttracker): " db_name
        db_name=${db_name:-projecttracker}

        read -p "Enter MySQL username: " db_user
        read -s -p "Enter MySQL password: " db_password
        echo ""

        # Attempt to create database
        echo "Creating database $db_name..."
        mysql -u "$db_user" -p"$db_password" -e "CREATE DATABASE IF NOT EXISTS \`$db_name\`;"

        if [ $? -eq 0 ]; then
            echo "Database created successfully."

            # Set environment variables
            echo "export FLASK_APP=main.py" > .env
            echo "export DATABASE_URL=mysql+pymysql://$db_user:$db_password@localhost/$db_name" >> .env
            echo "export SESSION_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(16))')" >> .env

            echo "Environment variables saved to .env file."
            source .env

            # Initialize database with Flask-Migrate
            echo "Initializing database with Flask-Migrate..."
            flask db init
            flask db migrate -m "Initial migration"
            flask db upgrade
        else
            echo "Failed to create database. You will need to set it up manually."
        fi
    fi
fi

echo "Setup complete!"
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Load environment variables: source .env"
echo "3. Run the application: flask run or gunicorn main:app"
