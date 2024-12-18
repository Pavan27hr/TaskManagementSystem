from flask import render_template, redirect, url_for, flash, session,request
from app import app, mysql, bcrypt
from app.forms import RegistrationForm, LoginForm
import MySQLdb


@app.route('/')
def home():
    # Initialize the form here
    register_form = RegistrationForm()
    login_form = LoginForm()

    return render_template('home.html', register_form=register_form, login_form=login_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()  # This is the form for registration
    login_form = LoginForm()  # This is the form for login

    if register_form.validate_on_submit():
        username = register_form.username.data
        email = register_form.email.data
        password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        
        cursor = mysql.connection.cursor()
        
        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            flash('Email already registered. Please use a different one.', 'danger')
            return redirect(url_for('register'))
        
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                       (username, email, password))
        mysql.connection.commit()
        cursor.close()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('home.html', register_form=register_form, login_form=login_form)  # Pass both forms here

@app.route('/login', methods=['GET', 'POST'])
def login():
    register_form = RegistrationForm()  # Add this
    login_form = LoginForm()
    
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]   
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    # Pass both forms to the template
    return render_template('home.html', register_form=register_form, login_form=login_form)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        status = request.form['status']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, title, category, status)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], title, category, status))
        mysql.connection.commit()
        cursor.close()

        flash('Task added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_task.html')


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    task = cursor.fetchone()

    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        status = request.form['status']

        cursor.execute("""
            UPDATE tasks SET title = %s, category = %s, status = %s WHERE id = %s
        """, (title, category, status, task_id))
        mysql.connection.commit()
        cursor.close()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    cursor.close()
    return render_template('edit_task.html', task=task)


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    status = request.args.get('status')
    date = request.args.get('date')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor here
    query = "SELECT id, title, category, status, date FROM tasks WHERE user_id = %s"
    params = [user_id]
    
    if status:
        query += " AND status = %s"
        params.append(status)
    if date:
        query += " AND DATE(date) = %s"
        params.append(date)

    cursor.execute(query, params)
    tasks = cursor.fetchall()  # This will now be a list of dictionaries
    cursor.close()
    
    return render_template('dashboard.html', tasks=tasks, status=status, date=date)