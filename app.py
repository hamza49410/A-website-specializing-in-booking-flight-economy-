from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    from_city = request.args.get('from', '')
    to_city = request.args.get('to', '')
    return render_template('results.html', from_city=from_city, to_city=to_city)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    return '<h2 style="text-align:center;margin-top:100px">✅ تم تأكيد حجزك بنجاح!</h2>'

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)