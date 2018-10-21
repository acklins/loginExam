from flask import Flask,render_template,request,redirect, session,flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'WeAreKeepingThis'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/process", methods =['post'])
def process():
    session ['firstname']= request.form['firstname']
    session ['lastname']= request.form['lastname']
    session ['email'] = request.form['email']
    session ['password']= request.form['password']
    session ['confirmpassword']=request.form['confirmpassword']

    if len(session['firstname']) < 1:
        flash("First Name cannot be blank :-)",'firstname') 

    elif len(session['firstname']) <=3:
        flash('Name must be 3+ characters', 'firstname')

    if len(session['lastname']) < 1:
        flash("Last Name cannot be blank :-)", 'lastname')

    elif len(session['lastname']) <=3:
        flash('Last Name must be 3+ characters', 'lastname')

    if len(session['email']) <1:
        flash('Email required', 'email')

    elif not EMAIL_REGEX.match(session['email']):
        flash('Email not valid', 'email')
       
    if len(session['password']) < 1:
        flash('Password cannot be blank!', 'password')

    elif len(session['password']) < 8:
        flash('Password must be 8+ characters', 'password')

    if session['confirmpassword'] != session['password']:
        flash('passwords do not match','confirmpassword')

    if '_flashes' in session.keys():
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    mysql = connectToMySQL('loginone')
    query = 'INSERT INTO user(firstname,lastname,email,password) VALUES(%(firstname)s, %(lastname)s, %(email)s, %(password_hash)s);'
    data = {
            'firstname': request.form['firstname'],
            'lastname': request.form['lastname'],
            'email': request.form['email'],
            'password_hash':pw_hash
    }
    new_email_id = mysql.query_db(query,data)
    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login', methods=['POST'])
def login():
    session ['email'] = request.form['email']
    session ['password']= request.form['password']
    mysql = connectToMySQL('loginone')
    query = 'SELECT * from user WHERE email = %(email)s;'
    data = { 'email': request.form['email']}
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['id'] = result[0]['id']
            return redirect('/loginprocess')
    flash('cannot log in')
    return redirect('/')

@app.route('/loginprocess')
def loginprocess():
    return render_template('login.html')

if __name__=="__main__":
    app.run(debug=True)


