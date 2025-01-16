from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)


# Route to display the form
@app.route("/")
def form():
    return render_template("form.html")


# Route to handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    # Get data from form
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Save to CSV
    with open("submissions.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, message])

    return redirect(url_for("thank_you"))


# Route to display a thank-you page
@app.route("/thank-you")
def thank_you():
    return "Thank you for your submission!"


# Route to view collected submissions (admin view)
@app.route("/submissions")
def view_submissions():
    data = []
    with open("submissions.csv", mode="r") as file:
        reader = csv.reader(file)
        data = list(reader)
    return render_template("submissions.html", submissions=data)


if __name__ == "__main__":
    app.run(debug=True)
