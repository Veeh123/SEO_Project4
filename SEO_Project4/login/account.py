from flask import Flask, render_template, url_for, flash, redirect, request, Markup
from forms import RegistrationForm
from flask_login import LoginManager
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
proxied = FlaskBehindProxy(app)  ## add this line
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = '48103c3f1e535f696813b3bcb1321b7b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/website")
def home():
    return render_template('website.html', subtitle='Home Page', text='This is the home page')

@app.route("/home")
def second_page():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

@app.route("/", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
      if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        email = request.form.get('email')
        user = User.query.filter_by(username=username).first()
        another_user = User.query.filter_by(email=email).first()
        print(user, another_user)
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            message = Markup("<h4>Username already taken. Click <a href='/login'>here</a> to login <br> Click <a href='/'>here</a> to sign-up with a different username</h4>")
            flash(message)
            return render_template('blank.html')
        elif another_user: # if a user is found, we want to redirect back to signup page so user can try again
            message = Markup("<h4>Email already used. Click <a href='/login'>here</a> to login <br> Click <a href='/'>here</a> to sign-up with a different email</h4>")
            flash(message)
            return render_template('blank.html')
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        #flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_name = request.form.get('username')
        user = User.query.filter_by(username=user_name).first()
        #if not user or not user.password:
        if request.form['username'] != user.username or request.form['password'] != user.password:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")