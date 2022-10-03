import sqlite3
import datetime
import re

from flask import Flask, flash, render_template, redirect, request
from flask_session import Session
from flask_mail import Mail, Message

# Turn file into flask application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'helloworld12603@gmail.com'
app.config['MAIL_PASSWORD'] = 'reywvndwazzeefqh'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Initialize mail here
mail = Mail(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Use sqlite3 db
db = sqlite3.connect("users.db", check_same_thread=False)
database = sqlite3.connect("blogs.db", check_same_thread=False)

# Home page


@app.route("/")
def index():
    return render_template("index.html")

# E-books page


@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        email = request.form.get("user-email")
        book = request.form.get("book-name")
        if not email:
            flash("this field is required")
            return render_template("books.html")

        new_book = "Hello Ashraf,"+"\nA new user want to buy your '"+book+"' e-book"+"\nhis email is "+email
        msg = Message("New book purchase", sender="helloworld12603@gmail.com", recipients=["ashraf.adel1105@gmail.com"])
        msg.body = new_book
        mail.send(msg)
        flash("We have received your request successfully")
        return render_template("books.html")
    else:
        return render_template("books.html")

# Apply for coaching page


@app.route("/apply", methods=["GET", "POST"])
def apply():
    # Check if user submitted the form
    if request.method == "POST":

        name = request.form.get("name")
        name2 = request.form.get("name2")
        email = request.form.get("email")
        number = request.form.get("number")
        goal = request.form.get("goal")
        age = request.form.get("age")
        category = request.form.get("category")
        full_name = name+" "+name2

        # Check if only email field has admin email. "or" is to make sure that all field are empty
        if email == "ashraf.adel1105@gmail.com" and not (name or name2 or number or goal != "Goal" or category != "Category"):
            # Run template to check users identity

            return render_template("check.html")

        elif name and name2 and number and age and email and goal != "Goal" and category != "Category":
            # Check if user gmail registered before

            same_user = db.execute("SELECT gmail FROM users")

            # Iterate over database to check for same gmail
            counter = 0
            for row in same_user:
                if row[0] == email:
                    counter += 1

            if counter > 0:
                flash("This Gmail already registered before!")
                return render_template("apply.html")

            # Refuse invalide email address format
            matched = re.fullmatch("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email)
            if not bool(matched):
                flash("Invalid email address!")
                return render_template("apply.html")

            # check that phone number exists
            if not bool(re.fullmatch("^01[0125][0-9]{8}$", number)):
                flash("Phone number doesn't exist!")
                return render_template("apply.html")

            # Add user data to table
            db.execute("INSERT INTO users(date, name, age, goal, category, gmail, number) VALUES (?,?,?,?,?,?,?)",
                       (datetime.datetime.now(), full_name, age, goal, category, email, number))
            db.commit()

            flash("Data Saved Successfully")

            # Sending message to admin that new user signed in
            user_info = {"Name": full_name, "Age": age, "Goal": goal, "Category": category,
                         "Gmail": email, "Phone Number": number}

            intro = "hello , Ashraf \n --User data--"

            # add each key and it's value to intro .items() is used to get each item(key,value) in dict
            for key, value in user_info.items():
                intro += "\n" + key + " : " + value

            msg = Message("New Client Applied!", sender="helloworld12603@gmail.com", recipients=["ashraf.adel1105@gmail.com"])
            msg.body = intro
            mail.send(msg)
            return render_template("apply.html")

        else:
            # Check if any field is empty return error and apply page again

            flash("All fields must be filled!")
            return render_template("apply.html")

    else:

        return render_template("apply.html")

# Admin check password page


@app.route("/check", methods=["POST", "GET"])
def check():
    # Identify admin identity

    if request.method == "GET":
        return render_template("check.html")

    else:
        password = request.form.get("pass")
        page = request.form.get("page-selected")

        if password == "Ashraf.1105":
            if page == "user-info":
                users = db.execute("SELECT * FROM users")
                flash("Welcome back, Ashraf")
                return render_template("users.html", users=users)
            elif page == "new-blog":
                return render_template("Add.html")
            elif page == "rem-blog":
                blogs = database.execute("SELECT * FROM blogs")
                return render_template("A-blogs.html", blogs=blogs)
        elif not password:
            flash("This field must be filled!")
            return render_template("check.html")
        else:
            flash("INCORRECT PASSWORD!")
            return render_template("check.html")


# redirect from any page that has users button to this page


@app.route("/users")
def users():
    users = db.execute("SELECT * FROM users")
    return render_template("users.html", users=users)

# Add new blog page


@app.route("/add", methods=["GET", "POST"])
def add():


    if request.method == "POST":
        head = request.form.get("head")
        body = request.form.get("body")
        if not head:
            flash("head must be filled")
            return render_template("add.html")
        elif not body:
            flash("body can't be empty")
            return render_template("add.html")

        database.execute("INSERT INTO blogs (header, body) VALUES(?, ?)", (head, body))
        database.commit()
        flash("blog added successfully")
        return render_template("add.html")

    return render_template("add.html")

# Blogs page


@app.route("/blogs")
def blogs():
    blogs = database.execute("SELECT * FROM blogs")
    return render_template("blogs.html", blogs=blogs)

# Remove blog as admin


@app.route("/remove", methods=["GET", "POST"])
def remove():
    if request.method == "POST":
        blog_number = request.form.get("id")
        database.execute("DELETE FROM blogs WHERE id = ?", [blog_number])
        database.commit()
        blogs = database.execute("SELECT * FROM blogs")
        return render_template("A-blogs.html", blogs=blogs)

    blogs = database.execute("SELECT * FROM blogs")
    return render_template("A-blogs.html", blogs=blogs)

# About page


@app.route("/about")
def about():
    return render_template("about.html")
