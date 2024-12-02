from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import mysql.connector
from mysql.connector import Error
import bcrypt
from PIL import Image
import io
from rembg import remove

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


        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
                       (username, email, hashed_password, is_admin))
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
    error_message = None  

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id, username, email, password, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):  
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = user[4]

                if user[4] == 1:  
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('index'))
            else:
                error_message = 'Invalid credentials, please try again.' 
        else:
            error_message = 'Invalid credentials, please try again.'  

    return render_template('login.html', error_message=error_message)


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


    post_interests = {}

    for post in user_posts:
        post_id = post[0]

        cursor.execute('''SELECT users.username 
                           FROM post_interests 
                           JOIN users ON post_interests.user_id = users.id
                           WHERE post_interests.post_id = %s''', (post_id,))
        interested_users = cursor.fetchall()
        post_interests[post_id] = [user[0] for user in interested_users]

    cursor.close()
    connection.close()

    return render_template('index.html', user_posts=user_posts, post_interests=post_interests)


@app.route('/edit/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    description = request.form['description']
    price = request.form['price']

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute('''UPDATE posts 
                       SET description = %s, price = %s 
                       WHERE id = %s AND user_id = %s''', 
                   (description, price, post_id, session['user_id']))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'message': 'Post updated successfully'})


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute('DELETE FROM post_interests WHERE post_id = %s', (post_id,))

 
    cursor.execute('DELETE FROM comments WHERE post_id = %s', (post_id,))


    cursor.execute('DELETE FROM posts WHERE id = %s AND user_id = %s', (post_id, session['user_id']))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))



@app.route('/buy')
def buy():

    if 'user_id' not in session:

        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute('''SELECT posts.id, posts.image, posts.description, posts.price, users.username, users.profile_pic
                       FROM posts 
                       JOIN users ON posts.user_id = users.id''')
    posts = cursor.fetchall()


    comments = {}
    for post in posts:
        cursor.execute('''SELECT comments.comment_text, users.username, users.profile_pic 
                           FROM comments 
                           JOIN users ON comments.user_id = users.id 
                           WHERE comments.post_id = %s''', (post[0],))
        comments[post[0]] = cursor.fetchall()


    user_has_interest = {}
    user_id = session.get('user_id')
    cursor.execute('''SELECT post_id FROM post_interests WHERE user_id = %s''', (user_id,))
    interested_posts = cursor.fetchall()
    interested_post_ids = [post[0] for post in interested_posts]

    for post in posts:
        post_id = post[0]
        user_has_interest[post_id] = post_id in interested_post_ids

    cursor.close()
    connection.close()

    return render_template('buy.html', posts=posts, comments=comments, user_has_interest=user_has_interest)




@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']


        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


        input_image = file.read()


        output_image = remove(input_image)


        image = Image.open(io.BytesIO(output_image))


        max_size = (800, 800)
        image.thumbnail(max_size)


        image.save(file_path, format="PNG", optimize=True, quality=85)


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
    if 'comment' not in request.form:
        return jsonify({'error': 'Missing comment text'}), 400

    comment_text = request.form['comment']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)",
                   (post_id, user_id, comment_text))
    connection.commit()


    cursor.execute('''SELECT comment_text, users.username, users.profile_pic 
                       FROM comments 
                       JOIN users ON comments.user_id = users.id 
                       WHERE comments.post_id = %s 
                       ORDER BY comments.id DESC LIMIT 1''', (post_id,))
    new_comment = cursor.fetchone()

    cursor.close()
    connection.close()

    if new_comment:
        return jsonify({
            'comment_text': new_comment[0],
            'username': new_comment[1],
            'profile_pic': new_comment[2] if new_comment[2] else 'default-profile.png'  # Default image if profile pic is not available
        })
    else:
        return jsonify({'error': 'Failed to add comment'}), 500

@app.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute('''SELECT comment_text, users.username, users.profile_pic 
                       FROM comments 
                       JOIN users ON comments.user_id = users.id 
                       WHERE comments.post_id = %s 
                       ORDER BY comments.id DESC''', (post_id,))
    comments = cursor.fetchall()

    cursor.close()
    connection.close()

    if comments:

        return jsonify({
            'comments': [{'comment_text': comment[0], 'username': comment[1], 'profile_pic': comment[2] or 'default-profile.png'} for comment in comments]
        })
    else:
        return jsonify({'error': 'No comments found'}), 404




@app.route('/edit_comment/<int:post_id>', methods=['POST'])
def edit_comment(post_id):
    data = request.get_json()
    username = data.get('username')
    comment_text = data.get('comment_text')
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute('''SELECT comments.id FROM comments 
                      JOIN users ON comments.user_id = users.id
                      WHERE comments.post_id = %s AND users.username = %s''', (post_id, username))
    comment = cursor.fetchone()

    if comment:
        cursor.execute('UPDATE comments SET comment_text = %s WHERE id = %s', (comment_text, comment[0]))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'success': True})
    else:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Comment not found or unauthorized'}), 403






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


from PIL import Image
import os

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute("SELECT username, email, profile_pic FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        profile_pic = request.files['profile_pic'] if 'profile_pic' in request.files else None
        

        if profile_pic:

            filename = secure_filename(profile_pic.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)


            with Image.open(profile_pic) as img:

                if img.mode == 'RGBA':
                    img = img.convert('RGB')  


                img.thumbnail((400, 400)) 


                img.save(image_path, format='JPEG', quality=85)  

            new_profile_pic = filename
        else:
            new_profile_pic = user[2] 


        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''UPDATE users 
                              SET username = %s, email = %s, password = %s, profile_pic = %s 
                              WHERE id = %s''', 
                           (username, email, hashed_password, new_profile_pic, session['user_id']))
        else:

            cursor.execute('''UPDATE users 
                              SET username = %s, email = %s, profile_pic = %s 
                              WHERE id = %s''', 
                           (username, email, new_profile_pic, session['user_id']))

        connection.commit()
        cursor.close()
        connection.close()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    cursor.close()
    connection.close()
    return render_template('profile.html', user=user)









@app.route('/add_interest/<int:post_id>', methods=['POST'])
def add_interest(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']


    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM post_interests WHERE post_id = %s AND user_id = %s', (post_id, user_id))
    existing_interest = cursor.fetchone()

    if existing_interest:

        flash('You have already shown interest in this post.', 'info')
        cursor.close()
        connection.close()
        return redirect(url_for('index'))  


    cursor.execute('INSERT INTO post_interests (post_id, user_id) VALUES (%s, %s)', (post_id, user_id))
    connection.commit()


    cursor.execute('UPDATE posts SET interest = interest + 1 WHERE id = %s', (post_id,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Your interest has been added!', 'success')
    return redirect(url_for('index'))  



if __name__ == '__main__':
    app.run(debug=True)
