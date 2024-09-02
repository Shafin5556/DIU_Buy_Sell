from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = 'static/uploads'


def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS posts
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        image TEXT,
                        description TEXT,
                        price TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS comments
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER,
                        user_id INTEGER,
                        comment_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(post_id) REFERENCES posts(id),
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

init_db()

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cur.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    
    return render_template('login.html')

# Home page
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT id, image, description, price 
                       FROM posts 
                       WHERE user_id = ?''', (session['user_id'],))
        user_posts = cur.fetchall()

    return render_template('index.html', user_posts=user_posts)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, session['user_id']))
        conn.commit()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))


# Buy page - display posts
@app.route('/buy')
def buy():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        # Get posts with user details
        cur.execute('''SELECT posts.id, posts.image, posts.description, posts.price, users.username
                       FROM posts JOIN users ON posts.user_id = users.id''')
        posts = cur.fetchall()

        # Get comments for each post
        comments = {}
        for post in posts:
            cur.execute('''SELECT comments.comment_text, users.username 
                           FROM comments JOIN users ON comments.user_id = users.id 
                           WHERE comments.post_id = ?''', (post[0],))
            comments[post[0]] = cur.fetchall()

    return render_template('buy.html', posts=posts, comments=comments)


# Sell page - create post
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO posts (user_id, image, description, price) VALUES (?, ?, ?, ?)",
                        (session['user_id'], filename, description, price))
            conn.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('buy'))
    
    return render_template('sell.html')

# Comment on a post
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    comment_text = request.form['comment']

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (?, ?, ?)",
                    (post_id, session['user_id'], comment_text))
        conn.commit()

    return redirect(url_for('buy'))

# User logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
