from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'skydeal123'

app.config['MYSQL_HOST'] = 'sql7.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql7825648'
app.config['MYSQL_PASSWORD'] = 'كلمة السر من الموقع'
app.config['MYSQL_DB'] = 'sql7825648'

mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()
    cur.close()
    return render_template('index.html', user=session.get('name'), flights=flights)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if email == 'admin@skydeal.com':
            return render_template('register.html', error='هاد الإيميل محجوز!')
        name = request.form['name']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password))
        mysql.connection.commit()
        cur.close()
        session['name'] = name
        session['email'] = email
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'admin@skydeal.com' and password == 'admin123':
            session['name'] = 'Admin'
            session['is_admin'] = True
            return redirect('/dashboard')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['name'] = user['full_name']
            session['email'] = user['email']
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/search')
def search():
    from_city = request.args.get('from', '')
    to_city = request.args.get('to', '')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flights WHERE from_city LIKE %s OR to_city LIKE %s",
                (f'%{from_city}%', f'%{to_city}%'))
    flights = cur.fetchall()
    cur.close()
    return render_template('results.html', from_city=from_city, to_city=to_city, flights=flights)

@app.route('/booking')
def booking():
    flight_id = request.args.get('id', 1)
    return render_template('booking.html', flight_id=flight_id)

@app.route('/confirm', methods=['POST'])
def confirm():
    if 'name' not in session:
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE email=%s", (session.get('email'),))
    user = cur.fetchone()
    user_id = user['user_id'] if user else 1
    flight_id = request.form.get('flight_id', 1)
    cur.execute("""
        INSERT INTO bookings 
        (user_id, flight_id, first_name, last_name, passport_number, nationality, seat_preference, meal_preference)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id, flight_id,
        request.form['first_name'],
        request.form['last_name'],
        request.form['passport'],
        request.form['nationality'],
        request.form['seat'],
        request.form['meal']
    ))
    mysql.connection.commit()
    cur.close()
    return redirect('/mybookings')

@app.route('/mybookings')
def mybookings():
    if 'name' not in session:
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE email=%s", (session.get('email'),))
    user = cur.fetchone()
    if user:
        cur.execute("""
            SELECT b.*, f.from_city, f.to_city, f.airline 
            FROM bookings b 
            JOIN flights f ON b.flight_id = f.flight_id 
            WHERE b.user_id = %s
        """, (user['user_id'],))
        bookings = cur.fetchall()
    else:
        bookings = []
    cur.close()
    return render_template('mybookings.html', bookings=bookings)

@app.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()
    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()
    cur.execute("SELECT full_name, email FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', flights=flights, bookings=bookings, users=users)

@app.route('/add_flight', methods=['POST'])
def add_flight():
    if not session.get('is_admin'):
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO flights (airline, from_city, to_city, old_price, new_price, discount, expires)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        request.form['airline'],
        request.form['from'],
        request.form['to'],
        request.form['old_price'],
        request.form['new_price'],
        request.form['discount'],
        request.form['expires']
    ))
    mysql.connection.commit()
    cur.close()
    return redirect('/dashboard')

@app.route('/delete_flight/<int:flight_id>')
def delete_flight(flight_id):
    if not session.get('is_admin'):
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM flights WHERE flight_id=%s", (flight_id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)