from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
import sqlite3
import os
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__, static_folder='static')

# Database setup
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create books table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            total_pages INTEGER,
            pages_read INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            notes TEXT,
            cover_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Google Books API key - you should use environment variables in production
GOOGLE_BOOKS_API_KEY = None  # Optional, can work without API key with limited quota

# API Routes
@app.route('/api/books', methods=['GET'])
def get_books():
    status = request.args.get('status', 'all')
    query = request.args.get('query', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM books"
    params = []
    
    where_clauses = []
    if status != 'all':
        where_clauses.append("status = ?")
        params.append(status)
    
    if query:
        where_clauses.append("(title LIKE ? OR author LIKE ?)")
        params.append(f"%{query}%")
        params.append(f"%{query}%")
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    sql += " ORDER BY created_at DESC"
    
    cursor.execute(sql, params)
    books = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def add_book():
    book_data = request.json
    
    title = book_data.get('title')
    author = book_data.get('author')
    
    if not title or not author:
        return jsonify({"message": "Title and author are required"}), 400
    
    # Convert string numbers to integers where applicable
    if book_data.get('total_pages'):
        book_data['total_pages'] = int(book_data['total_pages'])
    if book_data.get('pages_read'):
        book_data['pages_read'] = int(book_data['pages_read'])
    
    # Get book cover from Google Books API
    cover_url = get_book_cover(title, author)
    if cover_url:
        book_data['cover_url'] = cover_url
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Prepare SQL statement based on provided fields
    fields = []
    values = []
    placeholders = []
    
    for key, value in book_data.items():
        if key in ['title', 'author', 'genre', 'total_pages', 'pages_read', 'status', 'notes', 'cover_url']:
            fields.append(key)
            values.append(value)
            placeholders.append('?')
    
    sql = f"INSERT INTO books ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
    
    cursor.execute(sql, values)
    conn.commit()
    book_id = cursor.lastrowid
    
    # Get the newly created book
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = dict(cursor.fetchone())
    
    conn.close()
    return jsonify(book), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book_data = request.json
    
    # Convert string numbers to integers where applicable
    if book_data.get('total_pages'):
        book_data['total_pages'] = int(book_data['total_pages'])
    if book_data.get('pages_read'):
        book_data['pages_read'] = int(book_data['pages_read'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, check if the book exists
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"message": "Book not found"}), 404
    
    # Prepare SQL statement for update
    set_clauses = []
    values = []
    
    for key, value in book_data.items():
        if key in ['title', 'author', 'genre', 'total_pages', 'pages_read', 'status', 'notes']:
            set_clauses.append(f"{key} = ?")
            values.append(value)
    
    # Only update cover if title or author changed and we don't already have a cover
    if 'title' in book_data or 'author' in book_data:
        cursor.execute("SELECT cover_url FROM books WHERE id = ?", (book_id,))
        current_cover = cursor.fetchone()['cover_url']
        
        if not current_cover:
            cursor.execute("SELECT title, author FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            title = book_data.get('title', book['title'])
            author = book_data.get('author', book['author'])
            
            cover_url = get_book_cover(title, author)
            if cover_url:
                set_clauses.append("cover_url = ?")
                values.append(cover_url)
    
    sql = f"UPDATE books SET {', '.join(set_clauses)} WHERE id = ?"
    values.append(book_id)
    
    cursor.execute(sql, values)
    conn.commit()
    
    # Get updated book
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = dict(cursor.fetchone())
    
    conn.close()
    return jsonify(book)

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"message": "Book not found"}), 404
    
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Book deleted successfully"})

@app.route('/api/export', methods=['GET'])
def export_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
    books = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    if not books:
        return jsonify({"message": "No books to export"}), 404
    
    # Create DataFrame and export to CSV
    df = pd.DataFrame(books)
    
    # Format the timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reading_log_{timestamp}.csv"
    
    # Create CSV response
    csv_data = df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"
    
    return response

# Helper function to get book cover from Google Books API
def get_book_cover(title, author):
    try:
        query = f"{title} {author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        
        if GOOGLE_BOOKS_API_KEY:
            url += f"&key={GOOGLE_BOOKS_API_KEY}"
        
        response = requests.get(url)
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            volume_info = data['items'][0]['volumeInfo']
            
            if 'imageLinks' in volume_info and 'thumbnail' in volume_info['imageLinks']:
                # Convert HTTP to HTTPS to avoid mixed content warnings
                return volume_info['imageLinks']['thumbnail'].replace('http://', 'https://')
                
        return None
    except Exception as e:
        print(f"Error fetching book cover: {str(e)}")
        return None

# Serve static files and HTML
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)