from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'skydeal123'

users = {}

@app.route('/')
def home():
    return render_template('index.html', user=session.get('name'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        users[email] = {'name': name, 'password': password}
        session['name'] = name
        session['email'] = email
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            session['name'] = users[email]['name']
            session['email'] = email
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
    return render_template('results.html', from_city=from_city, to_city=to_city)

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    if 'name' not in session:
        return redirect('/login')
    
    booking = {
        'from': request.args.get('from', 'الرياض'),
        'to': request.args.get('to', 'دبي'),
        'name': request.form['first_name'] + ' ' + request.form['last_name'],
        'seat': request.form['seat'],
        'meal': request.form['meal'],
    }
    
    if 'bookings' not in session:
        session['bookings'] = []
    
    bookings = session['bookings']
    bookings.append(booking)
    session['bookings'] = bookings
    
    return redirect('/mybookings')

@app.route('/mybookings')
def mybookings():
    if 'name' not in session:
        return redirect('/login')
    bookings = session.get('bookings', [])
    return render_template('mybookings.html', bookings=bookings)
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)
