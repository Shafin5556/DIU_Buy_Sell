from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  
        database='buy_sell_db'
    )

def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT 0
                     )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        image VARCHAR(255),
                        description TEXT,
                        price DECIMAL(10, 2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                     )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        post_id INT,
                        user_id INT,
                        comment_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(post_id) REFERENCES posts(id),
                        FOREIGN KEY(user_id) REFERENCES users(id)
                     )''')
    connection.commit()
    cursor.close()
    connection.close()

init_db()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 1 if username == 'admin' and password == 'admin' else 0

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)", (username, email, password, is_admin))
        connection.commit()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = username
            session['is_admin'] = is_admin
            flash('Registration successful! You are now logged in.', 'success')

            if is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            flash('Login successful!', 'success')

            if user[4] == 1:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT id, image, description, price 
                       FROM posts 
                       WHERE user_id = %s''', (session['user_id'],))
    user_posts = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('index.html', user_posts=user_posts)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s AND user_id = %s', (post_id, session['user_id']))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/buy')
def buy():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT posts.id, posts.image, posts.description, posts.price, users.username
                       FROM posts JOIN users ON posts.user_id = users.id''')
    posts = cursor.fetchall()

    comments = {}
    for post in posts:
        cursor.execute('''SELECT comments.comment_text, users.username 
                           FROM comments JOIN users ON comments.user_id = users.id 
                           WHERE comments.post_id = %s''', (post[0],))
        comments[post[0]] = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('buy.html', posts=posts, comments=comments)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO posts (user_id, image, description, price) VALUES (%s, %s, %s, %s)",
                        (session['user_id'], filename, description, price))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Post created successfully!', 'success')
        return redirect(url_for('buy'))
    
    return render_template('sell.html')

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    comment_text = request.form['comment']
    user_id = session['user_id']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)",
                    (post_id, user_id, comment_text))
    connection.commit()
    cursor.execute('''SELECT comment_text, users.username 
                       FROM comments JOIN users ON comments.user_id = users.id 
                       WHERE comments.post_id = %s AND comments.user_id = %s 
                       ORDER BY comments.id DESC LIMIT 1''', (post_id, user_id))
    new_comment = cursor.fetchone()
    cursor.close()
    connection.close()

    return jsonify({
        'comment_text': new_comment[0],
        'username': new_comment[1]
    })

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT posts.id, posts.image, posts.description, posts.price, users.username
                       FROM posts JOIN users ON posts.user_id = users.id''')
    posts = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin.html', posts=posts)

@app.route('/admin/delete/<int:post_id>', methods=['POST'])
def admin_delete_post(post_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
