from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import csv

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")  # Replace with a secure key

# Pepper: A global secret for extra password security
PEPPER = os.getenv("PEPPER", "a_very_secret_pepper")  # Replace with a secure value

# Admin creation code (set this as an environment variable)
ADMIN_CREATION_CODE = os.getenv("ADMIN_CREATION_CODE", "default_admin_code")  # Replace with a secure code

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admins.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database Model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(32), nullable=False)  # Unique salt for each user


# Initialize the database
with app.app_context():
    db.create_all()


# Function to hash a password with salt and pepper
def hash_password(password, salt):
    return bcrypt.hashpw((password + PEPPER).encode('utf-8'), salt)


# Function to verify a password
def verify_password(stored_hash, password, salt):
    return stored_hash == bcrypt.hashpw((password + PEPPER).encode('utf-8'), salt)


# Main page
@app.route("/")
def main():
    return render_template("main.html")


# Route to display the form
@app.route("/form")
def form():
    return render_template("form.html")


# Route to handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Save to CSV
    with open("submissions.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, message])

    return redirect(url_for("thank_you"))


# Thank-you page
@app.route("/thank-you")
def thank_you():
    return "Thank you for your submission!"


# Create an admin account (secured)
@app.route("/create-admin", methods=["GET", "POST"])
def create_admin():
    if request.method == "POST":
        admin_code = request.form["admin_code"]
        if admin_code != ADMIN_CREATION_CODE:
            flash("Invalid admin creation code.")
            return redirect(url_for("create_admin"))

        username = request.form["username"]
        password = request.form["password"]
        salt = bcrypt.gensalt()
        password_hash = hash_password(password, salt)
        admin = Admin(username=username, password_hash=password_hash, salt=salt)
        db.session.add(admin)
        db.session.commit()
        flash("Admin created successfully!")
        return redirect(url_for("login"))

    return render_template("create_admin.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
        if verify_password(admin.password_hash, password, admin.salt):
            session["admin"] = username
            return redirect(url_for("view_submissions"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")


# Admin view for submissions
@app.route("/submissions")
def view_submissions():
    if "admin" not in session:
        flash("Unauthorized access. Please log in.")
        return redirect(url_for("login"))
    data = []
    try:
        with open("submissions.csv", mode="r") as file:
            reader = csv.reader(file)
            data = list(reader)
    except FileNotFoundError:
        flash("No submissions found.")
        return redirect(url_for("form"))
    return render_template("submissions.html", submissions=data)


# Logout route
@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
