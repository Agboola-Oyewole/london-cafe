import smtplib
import os
from functools import wraps
from flask_gravatar import Gravatar
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from datetime import date
from sqlalchemy import and_
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from the_email import Email
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
app = Flask(__name__)
load_dotenv()

app.secret_key = os.environ.get('APP_KEY')
SECRET_URL = os.environ.get('SECRET_PASS')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://london_cafes_wifi_user:YHagTrti66JZ5qHiP9W1Xx3IQXoRLMfc@dpg-cj91nd2vvtos738cacd0-a.oregon-postgres.render.com/london_cafes_wifi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
# Connect to Database
db = SQLAlchemy(app)
n = None


year = date.today().strftime("%Y")
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

login_manager = LoginManager()
login_manager.init_app(app)
admin_yes = False


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    posts = relationship("Cafe", back_populates="author", lazy='subquery')


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    author = relationship("User", back_populates="posts", lazy='subquery')
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


@app.route('/', methods=['GET', 'POST'])
def home_page():
    global admin_yes, n
    n = None
    try:
        if current_user.id == 1:
            admin_yes = True
        else:
            admin_yes = False
    except AttributeError:
        admin_yes = False
    with app.app_context():
        page = request.args.get('page', 1, type=int)

    if request.method == 'POST':
        n = None
        wifi = request.form.get('select1')
        toilet = request.form.get('select2')
        sockets = request.form.get('select3')
        calls = request.form.get('select4')
        all_the_cafes = db.session.query(Cafe).filter(
            and_(Cafe.has_wifi == wifi, Cafe.has_toilet == toilet, Cafe.has_sockets == sockets,
                 Cafe.can_take_calls == calls)).paginate(page=page, per_page=100)
        n = 0
        for cafe in all_the_cafes:
            if cafe:
                n = 4
            else:
                n += 1
        print(n)

    else:
        all_the_cafes = Cafe.query.paginate(page=page, per_page=5)
        # count = len(all_the_cafes)
    return render_template('index.html', cafes=all_the_cafes, date=date,
                           logged_in=current_user.is_authenticated, user=current_user, year=year, admin=admin_yes, n=n)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        repeated_passwords = request.form.get('repeat')
        if password == repeated_passwords:
            hashed_password = generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=8)

            details = db.session.execute(db.select(User).where(User.email == email)).scalar()
            if details:
                return redirect(url_for('login', message=flash('This email already exists. Log In instead.')))
            else:
                new_user = User()
                new_user.name = name
                new_user.email = email
                new_user.password = hashed_password

                db.session.add(new_user)
                db.session.commit()

                already_logged = db.session.execute(db.select(User).where(User.email == email)).scalar()
                if already_logged:
                    login_user(already_logged)
                    Email(user=current_user.email, name=current_user.name)
                    return redirect(url_for("home_page"))

        else:
            flash("That passwords don't match, Please try again!")

    return render_template("register.html", logged_in=current_user.is_authenticated, user=current_user, year=year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        with app.app_context():
            details = db.session.execute(db.select(User).where(User.email == email)).scalar()
            if details:
                if check_password_hash(pwhash=details.password, password=password):
                    login_user(details)
                    return redirect(url_for('home_page'))
                else:
                    flash('Password Incorrect, Please try again!')
            else:
                flash("That email doesn't exist, Please try again!")

    return render_template("login.html", logged_in=current_user.is_authenticated, user=current_user, year=year)


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    edit = True
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        with app.app_context():
            details = db.session.execute(db.select(User).where(User.email == email)).scalar()
            if details:
                if check_password_hash(pwhash=details.password, password=password):
                    login_user(details)
                    return redirect(url_for('home_page'))
                else:
                    flash('Password Incorrect, Please try again!')
            else:
                flash("That email doesn't exist, Please try again!")

    return render_template("login.html", logged_in=current_user.is_authenticated, user=current_user, edit=edit,
                           year=year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        my_email = os.getenv('FIRST_EMAIL')
        password = os.getenv('SECRET_KEY')
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                                to_addrs=os.getenv('SECOND_EMAIL'),
                                msg=f"Subject:{subject}\n\nFrom: {name} "
                                    f"\nFrom Email Address: {email} \n\n"
                                    f"Message: {message}")
        return redirect(url_for('home_page'))

    return render_template('contact.html', logged_in=current_user.is_authenticated, user=current_user, year=year)


@app.route('/about')
def about():
    return render_template('about.html', logged_in=current_user.is_authenticated, user=current_user, year=year)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_cafe():
    if request.method == 'POST':
        with app.app_context():
            name = request.form.get('name')
            map_url = request.form.get('map')
            img_url = request.form.get('url')
            location = request.form.get('location')
            seats = request.form.get('seats')
            has_toilet = request.form.get('toilet')
            has_wifi = request.form.get('wifi')
            has_sockets = request.form.get('sockets')
            can_take_calls = request.form.get('calls')
            coffee_price = '£' + request.form.get('coffee_price')

            item = Cafe(name=name,
                        map_url=map_url,
                        img_url=img_url,
                        location=location,
                        seats=seats,
                        has_toilet=bool(int(has_toilet)),
                        has_wifi=bool(int(has_wifi)),
                        has_sockets=bool(int(has_sockets)),
                        can_take_calls=bool(int(can_take_calls)),
                        coffee_price=coffee_price,
                        author=current_user,
                        date=date.today().strftime("%B %d, %Y")
                        )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('home_page'))
    return render_template('add.html', logged_in=current_user.is_authenticated, user=current_user, year=year)


@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_to_delete = Cafe.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home_page'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        password = request.form.get('current')
        new_password = request.form.get('new')
        repeated = request.form.get('new_again')
        if check_password_hash(pwhash=current_user.password, password=password):
            if new_password == repeated:
                hashed_password = generate_password_hash(password=new_password, method="pbkdf2:sha256", salt_length=8)
                user = db.session.execute(db.select(User).where(User.password == current_user.password)).scalar()
                user.password = hashed_password
                db.session.commit()
                flash("Password successfully changed!", 'success')
            else:
                flash("New password doesn't match the repeated password, Please try again!", 'error')
        else:
            flash("Password doesn't match your current password, Please try again!", 'error')

    return render_template('settings.html', logged_in=current_user.is_authenticated, user=current_user, year=year)


if __name__ == '__main__':
    app.run(debug=True)
