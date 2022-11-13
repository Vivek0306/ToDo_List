from pydoc import render_doc
from click import password_option
from flask import Flask, request, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import false


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50))
    password = db.Column(db.String(50))
    tasks = db.relationship('ToDo', backref='user')

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route("/")
def index():
    if not session.get("uname"):
        return redirect("/login")
    else:
        user = User.query.filter_by(uname = session["uname"]).first()
        todo_list = ToDo.query.filter_by(user_id = user.id)
        return render_template('main.html', todo_list=todo_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # session["uname"] = request.form.get("uname")
        uname = request.form.get("uname")
        password = request.form.get("password")
        # user = User.query.filter_by(uname = session["uname"]).first()
        user = User.query.filter_by(uname = uname).first()
        if user:
            if check_password_hash(user.password, password):
                session["uname"] = uname
                return redirect("/")
            else:
                error = "Invalid username or password"
                return render_template('login.html', error=error)
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        uname = request.form.get("uname")
        password = request.form.get("password")
        if uname and password:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = User(uname=uname, password=hash)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
        else:
            error = "Please enter the username and password"
            return render_template('register.html', error=error)

    return render_template('register.html')

@app.route("/logout")
def logout():
    session["uname"] = None
    return redirect("/")

@app.route("/add", methods=["POST"])
def add():
    user = User.query.filter_by(uname = session["uname"]).first()
    title = request.form.get("title")
    new_todo = ToDo(title=title, complete=False, user_id = user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = ToDo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = ToDo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)