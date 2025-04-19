# 📚 Personal Reading Log

A full-stack web application to track your reading progress, manage your book collection, and export your reading data.

![Personal Reading Log Screenshot](https://via.placeholder.com/800x450)

## 📝 Overview

Personal Reading Log is a Flask and JavaScript web application that lets you:
- Track books you want to read, are currently reading, or have finished
- Monitor reading progress with visual progress bars
- Search and filter your book collection
- Automatically fetch book covers from Google Books API
- Export your reading data to CSV format

## ✨ Features

- **Book Management**
  - Add new books with title, author, genre, and page information
  - Track reading progress by pages read
  - Add personal notes for each book
  - Automatically fetch book covers from Google Books API
  - Edit and delete book entries

- **Organization & Filtering**
  - Filter books by reading status (To Read, Reading, Finished)
  - Search books by title or author
  - View reading progress with visual progress bars

- **Data Export**
  - Export your entire reading log to CSV format
  - Downloaded CSV includes timestamp for version control

## 🛠️ Technology Stack

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript (Vanilla JS)
  - Responsive design for mobile and desktop

- **Backend**:
  - Python 3.x
  - Flask web framework
  - SQLite database
  - Pandas for data export
  - Requests library for external API calls

- **External APIs**:
  - Google Books API for book cover images

## 📋 Project Structure

```
personal-reading-log/
├── app.py                # Flask backend application
├── index.html            # Main HTML page
├── books.db              # SQLite database
├── static/
│   ├── app.js            # Frontend JavaScript
│   ├── style.css         # CSS styles
│   └── placeholder.png   # Default book cover image
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/personal-reading-log.git
   cd personal-reading-log
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

### Required Python Packages

- Flask
- SQLite3 (included in Python standard library)
- requests
- pandas

You can install all dependencies using:
```bash
pip install flask requests pandas
```

## 📦 Deployment

This application has been deployed using Render. The deployment process is straightforward:

### Deploying to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add environment variables if needed (e.g., `GOOGLE_BOOKS_API_KEY`)
5. Deploy!

### Environment Variables

For production, consider setting:
- `GOOGLE_BOOKS_API_KEY`: Your Google Books API key (optional)
- `FLASK_ENV`: Set to `production` in production environments

## 🔧 Customization

### Google Books API

The application can work without a Google Books API key, but you may encounter rate limiting. To add your own API key:

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Books API
3. Update the `GOOGLE_BOOKS_API_KEY` variable in `app.py`

### Database

The application uses SQLite by default, which is suitable for personal use. For multi-user deployment, consider upgrading to PostgreSQL or MySQL.

## 📱 Usage Guide

1. **Adding a Book**:
   - Click "Add New Book"
   - Fill in the book details (title and author are required)
   - Click "Save Book"

2. **Tracking Reading Progress**:
   - Edit a book
   - Update the "Pages Read" field
   - The progress bar will automatically update

3. **Filtering Books**:
   - Use the dropdown to filter by status
   - Use the search box to find books by title or author

4. **Exporting Data**:
   - Click "Export to CSV"
   - The browser will download a timestamped CSV file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google Books API](https://developers.google.com/books) for book cover images
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Render](https://render.com/) for hosting services

## 📬 Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/your-username/personal-reading-log](https://github.com/your-username/personal-reading-log)

---

Happy reading! 📚