Library Management System

A full-stack, single-page web application for managing a small library. This project includes features for managing books, members, and loans, all powered by a Python API and a MySQL database.

Features

Book Management: Add new books and view a complete list of all available books, including their author, category, and available copies.

Member Management: Register new library members and view a list of all current members and their contact information.

Loan Management:

Issue books to members with a specific due date.

View a real-time list of all currently issued books.

Return books, which automatically updates the book's copy count and removes the loan from the active list.

Technology Stack

Backend: Python (Flask)

Database: MySQL

Frontend: HTML, JavaScript (Fetch API), Tailwind CSS

Runtime: Node.js (for live-server)

Prerequisites

Before you begin, ensure you have the following installed on your system:

Python 3.10+ (and pip)

[suspicious link removed] (Make sure the server is running)

Node.js (which includes npm)

Installation & Setup

Follow these steps to get your local development environment set up and running.
1. Clone the Repository

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME


2. Database Setup

Log in to your MySQL server (from the command line or a GUI like MySQL Workbench).

mysql -u root -p


Run the database.sql script to create the library database, all necessary tables, and insert the sample data.

SOURCE /path/to/your/project/database.sql;


3. Backend Setup

Navigate to the backend directory.

cd backend


Create a Python virtual environment.

# For Windows
python -m venv venv

# For macOS/Linux
python3 -m venv venv


Activate the virtual environment.

# For Windows
.\venv\Scripts\activate

# For macOS/Linux
source venv/bin/activate


Install the required Python packages.

pip install -r requirements.txt


4. Frontend Setup

Open a new, separate terminal.

Navigate to the frontend directory.

cd frontend


Install live-server, a simple development server with live-reload.

npm install -g live-server


🔐 Configuration (CRITICAL)

This project uses a .env file to securely store your database password.

In the backend folder, create a new file named .env

Copy and paste the following into the .env file, replacing the values with your own MySQL credentials.

DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="YOUR_MYSQL_PASSWORD"
DB_NAME="library"


The .gitignore file is already set up to ignore this file, so you will never accidentally upload your password to GitHub.

Running the Application

You must have two terminals open to run the full application.

Terminal 1: Run the Backend (Flask API)

Make sure you are in the backend directory.

Make sure your virtual environment is activated.

Run the Python server.

python backend.py


You should see * Running on http://127.0.0.1:5000. Leave this terminal running.

Terminal 2: Run the Frontend (Live Server)

Make sure you are in the frontend directory.

Run live-server.

live-server


This will automatically open your default web browser to http://127.0.0.1:8080 (or a similar port), and you can now use the application.

API Endpoints

GET /api/books: Get all books.

POST /api/books: Add a new book.

GET /api/members: Get all members.

POST /api/members: Add a new member.

GET /api/loans: Get all active loans.

POST /api/issue: Issue a new book.

PUT /api/return/<int:issue_id>: Return a book.
