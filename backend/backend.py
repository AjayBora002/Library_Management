import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import date

# --- IMPORTANT ---
db_config = {
    'host': 'localhost',
    'database': 'library', # <-- Changed to 'library'
    'user': 'root', # <-- Change this
    'password': '0plm9okn' # <-- Change this
}
# --- IMPORTANT ---

app = Flask(__name__)
CORS(app)

def create_db_connection():
    """Creates a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection

# ========================================
# BOOK ENDPOINTS
# ========================================

@app.route('/api/books', methods=['GET'])
def get_books():
    """Fetches all books from the database."""
    books = []
    connection = create_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    query = "SELECT BOOK_ID, category, NAME, AUTHOR, COPIES FROM books ORDER BY NAME"
    
    try:
        cursor.execute(query)
        books = cursor.fetchall()
    except Error as e:
        print(f"Error fetching books: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
        
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def add_book():
    """Adds a new book to the database."""
    data = request.get_json()
    
    required_fields = ['BOOK_ID', 'NAME', 'AUTHOR', 'category', 'COPIES']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor()
    
    query = """
        INSERT INTO books (BOOK_ID, category, NAME, AUTHOR, COPIES)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (
            data['BOOK_ID'], data['category'], data['NAME'],
            data['AUTHOR'], data['COPIES']
        ))
        connection.commit()
        return jsonify({"message": "Book added successfully", "BOOK_ID": data['BOOK_ID']}), 201
        
    except Error as e:
        print(f"Error adding book: {e}")
        connection.rollback()
        if e.errno == 1062:
            return jsonify({"error": f"Error: Book ID '{data['BOOK_ID']}' already exists."}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ========================================
# MEMBER ENDPOINTS (NEW)
# ========================================

@app.route('/api/members', methods=['GET'])
def get_members():
    """Fetches all members from the database."""
    members = []
    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    query = "SELECT USER_ID, NAME, CONTACT FROM members ORDER BY NAME"
    
    try:
        cursor.execute(query)
        members = cursor.fetchall()
    except Error as e:
        print(f"Error fetching members: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
        
    return jsonify(members)

@app.route('/api/members', methods=['POST'])
def add_member():
    """Adds a new member to the database."""
    data = request.get_json()
    
    required_fields = ['USER_ID', 'NAME', 'PASSWORD', 'CONTACT']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor()
    
    query = """
        INSERT INTO members (USER_ID, NAME, PASSWORD, CONTACT)
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (
            data['USER_ID'], data['NAME'], data['PASSWORD'], data['CONTACT']
        ))
        connection.commit()
        return jsonify({"message": "Member added successfully", "USER_ID": data['USER_ID']}), 201
        
    except Error as e:
        print(f"Error adding member: {e}")
        connection.rollback()
        if e.errno == 1062:
            return jsonify({"error": f"Error: User ID '{data['USER_ID']}' already exists."}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# ========================================
# LOAN ENDPOINTS (NEW)
# ========================================

@app.route('/api/loans', methods=['GET'])
def get_active_loans():
    """Fetches all active loans (status = 'Issued')."""
    loans = []
    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    # Join tables to get book and member names
    # *** UPDATED to select the new 'fine' column ***
    query = """
        SELECT ir.ISSUE_ID, ir.BOOK_ID, b.NAME as book_name, ir.USER_ID, m.NAME as member_name, 
               ir.issue_date, ir.due_date, ir.fine
        FROM issue_return ir
        JOIN books b ON ir.BOOK_ID = b.BOOK_ID
        JOIN members m ON ir.USER_ID = m.USER_ID
        WHERE ir.status = 'Issued'
        ORDER BY ir.due_date
    """
    
    try:
        cursor.execute(query)
        # Convert date objects to strings for JSON serialization
        loans = cursor.fetchall()
        for loan in loans:
            loan['issue_date'] = loan['issue_date'].isoformat()
            loan['due_date'] = loan['due_date'].isoformat()
            loan['fine'] = str(loan['fine']) # <-- NEW: Convert Decimal to string
    except Error as e:
        print(f"Error fetching loans: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
        
    return jsonify(loans)

@app.route('/api/issue', methods=['POST'])
def issue_book():
    """Issues a book to a member."""
    data = request.get_json()
    
    required_fields = ['BOOK_ID', 'USER_ID', 'due_date']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    try:
        # Start transaction
        connection.start_transaction()

        # 1. Check if book has available copies
        cursor.execute("SELECT COPIES FROM books WHERE BOOK_ID = %s FOR UPDATE", (data['BOOK_ID'],))
        book = cursor.fetchone()
        
        if not book:
            return jsonify({"error": "Book ID not found"}), 404
        if book['COPIES'] <= 0:
            return jsonify({"error": "No available copies of this book to issue"}), 400

        # 2. Update book copies (decrement)
        cursor.execute("UPDATE books SET COPIES = COPIES - 1 WHERE BOOK_ID = %s", (data['BOOK_ID'],))

        # 3. Create new loan record
        # *** This query is still correct, as 'fine' has a default value ***
        insert_loan_query = """
            INSERT INTO issue_return (BOOK_ID, USER_ID, due_date, status)
            VALUES (%s, %s, %s, 'Issued')
        """
        cursor.execute(insert_loan_query, (data['BOOK_ID'], data['USER_ID'], data['due_date']))
        
        # Commit transaction
        connection.commit()
        return jsonify({"message": "Book issued successfully"}), 201

    except Error as e:
        connection.rollback()
        print(f"Error issuing book: {e}")
        # Check for foreign key constraint violation (e.g., bad USER_ID)
        if e.errno == 1452:
             return jsonify({"error": "Invalid Book ID or User ID"}), 400
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/return/<int:issue_id>', methods=['PUT'])
def return_book(issue_id):
    """Returns a book based on the issue_id."""
    connection = create_db_connection()
    if connection is None: return jsonify({"error": "Database connection failed"}), 500
    cursor = connection.cursor(dictionary=True)

    try:
        # Start transaction
        connection.start_transaction()

        # 1. Get the loan details, and lock the row
        cursor.execute("SELECT BOOK_ID, status FROM issue_return WHERE ISSUE_ID = %s FOR UPDATE", (issue_id,))
        loan = cursor.fetchone()

        if not loan:
            return jsonify({"error": "Loan ID not found"}), 404
        if loan['status'] == 'Returned':
            return jsonify({"error": "This book has already been returned"}), 400

        # 2. Update the loan record
        # *** We could add fine calculation logic here, but for now just mark as returned ***
        cursor.execute(
            "UPDATE issue_return SET status = 'Returned', return_date = %s WHERE ISSUE_ID = %s",
            (date.today().isoformat(), issue_id)
        )

        # 3. Update book copies (increment)
        cursor.execute("UPDATE books SET COPIES = COPIES + 1 WHERE BOOK_ID = %s", (loan['BOOK_ID'],))

        # Commit transaction
        connection.commit()
        return jsonify({"message": "Book returned successfully"}), 200

    except Error as e:
        connection.rollback()
        print(f"Error returning book: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    # Runs the Flask server
    app.run(debug=True, port=5000)

