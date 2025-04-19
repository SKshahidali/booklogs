document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const addBookBtn = document.getElementById('add-book-btn');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const bookFormContainer = document.getElementById('book-form-container');
    const bookForm = document.getElementById('book-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const booksContainer = document.getElementById('books-container');
    const statusFilter = document.getElementById('status-filter');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    // API endpoint base URL - update this with your actual domain when deployed
    const API_URL = '/api';

    // Show/hide book form
    addBookBtn.addEventListener('click', () => {
        bookFormContainer.classList.remove('hidden');
        bookForm.reset();
    });

    cancelBtn.addEventListener('click', () => {
        bookFormContainer.classList.add('hidden');
    });

    // Handle book form submission
    bookForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(bookForm);
        const bookData = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch(`${API_URL}/books`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(bookData)
            });
            
            if (response.ok) {
                bookFormContainer.classList.add('hidden');
                fetchBooks();
            } else {
                const error = await response.json();
                alert(`Error: ${error.message || 'Failed to add book'}`);
            }
        } catch (error) {
            console.error('Error adding book:', error);
            alert('Failed to add book. Please try again.');
        }
    });

    // Export books to CSV
    exportCsvBtn.addEventListener('click', () => {
        window.location.href = `${API_URL}/export`;
    });

    // Filter books by status and search
    const filterBooks = () => {
        const status = statusFilter.value;
        const query = searchInput.value.trim();
        
        fetchBooks(status, query);
    };

    statusFilter.addEventListener('change', filterBooks);
    searchBtn.addEventListener('click', filterBooks);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            filterBooks();
        }
    });

    // Fetch books from API
    async function fetchBooks(status = 'all', query = '') {
        booksContainer.innerHTML = '<div class="loading">Loading books...</div>';
        
        try {
            const url = new URL(`${API_URL}/books`);
            if (status !== 'all') url.searchParams.append('status', status);
            if (query) url.searchParams.append('query', query);
            
            const response = await fetch(url);
            
            if (response.ok) {
                const books = await response.json();
                displayBooks(books);
            } else {
                booksContainer.innerHTML = '<div class="loading">Failed to load books.</div>';
            }
        } catch (error) {
            console.error('Error fetching books:', error);
            booksContainer.innerHTML = '<div class="loading">Failed to load books. Please try again later.</div>';
        }
    }

    // Display books in the UI
    function displayBooks(books) {
        if (books.length === 0) {
            booksContainer.innerHTML = '<div class="loading">No books found.</div>';
            return;
        }
        
        booksContainer.innerHTML = '';
        
        books.forEach(book => {
            const progress = book.total_pages > 0 ? 
                Math.min(100, Math.round((book.pages_read / book.total_pages) * 100)) : 0;
            
            const bookCard = document.createElement('div');
            bookCard.className = 'book-card';
            bookCard.innerHTML = `
                <div class="book-cover">
                    <img src="${book.cover_url || 'static/placeholder.png'}" alt="${book.title} cover">
                </div>
                <div class="book-details">
                    <h3 class="book-title">${book.title}</h3>
                    <p class="book-author">by ${book.author}</p>
                    <div class="book-meta">
                        <span>${book.genre || 'No genre'}</span>
                        <span class="status ${book.status}">${formatStatus(book.status)}</span>
                    </div>
                    ${book.total_pages ? `
                        <div class="progress-container">
                            <div class="progress-text">${book.pages_read} of ${book.total_pages} pages (${progress}%)</div>
                            <div class="progress-bar">
                                <div class="progress" style="width: ${progress}%"></div>
                            </div>
                        </div>
                    ` : ''}
                    ${book.notes ? `<div class="book-notes">${book.notes}</div>` : ''}
                    <div class="book-actions">
                        <button class="edit-btn" data-id="${book.id}">Edit</button>
                        <button class="delete-btn" data-id="${book.id}">Delete</button>
                    </div>
                </div>
            `;
            
            booksContainer.appendChild(bookCard);
            
            // Add event listeners for edit and delete buttons
            const editBtn = bookCard.querySelector('.edit-btn');
            const deleteBtn = bookCard.querySelector('.delete-btn');
            
            editBtn.addEventListener('click', () => editBook(book));
            deleteBtn.addEventListener('click', () => deleteBook(book.id));
        });
    }

    // Format status for display
    function formatStatus(status) {
        switch (status) {
            case 'to-read': return 'To Read';
            case 'reading': return 'Reading';
            case 'finished': return 'Finished';
            default: return status;
        }
    }

    // Edit book
    async function editBook(book) {
        // Populate form with book data
        document.getElementById('title').value = book.title;
        document.getElementById('author').value = book.author;
        document.getElementById('genre').value = book.genre || '';
        document.getElementById('total-pages').value = book.total_pages || '';
        document.getElementById('pages-read').value = book.pages_read || '';
        document.getElementById('status').value = book.status;
        document.getElementById('notes').value = book.notes || '';
        
        // Change form submit handler to update instead of create
        const originalSubmitHandler = bookForm.onsubmit;
        
        bookForm.onsubmit = async (e) => {
            e.preventDefault();
            
            const formData = new FormData(bookForm);
            const bookData = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch(`${API_URL}/books/${book.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(bookData)
                });
                
                if (response.ok) {
                    bookFormContainer.classList.add('hidden');
                    fetchBooks();
                    
                    // Reset form submit handler
                    bookForm.onsubmit = originalSubmitHandler;
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.message || 'Failed to update book'}`);
                }
            } catch (error) {
                console.error('Error updating book:', error);
                alert('Failed to update book. Please try again.');
            }
        };
        
        // Show form
        bookFormContainer.classList.remove('hidden');
    }

    // Delete book
    async function deleteBook(id) {
        if (!confirm('Are you sure you want to delete this book?')) {
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/books/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                fetchBooks();
            } else {
                const error = await response.json();
                alert(`Error: ${error.message || 'Failed to delete book'}`);
            }
        } catch (error) {
            console.error('Error deleting book:', error);
            alert('Failed to delete book. Please try again.');
        }
    }

    // Initial load
    fetchBooks();
});