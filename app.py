from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from main import main
from send_mail import send_email
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usernname = db.Column(db.String(200), unique=True, nullable = False)
    email = db.Column(db.String(200), unique = True, nullable = False)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return "<User %r>" % self.usernname

@app.route("/", methods=["POST", "GET"])
def home():
    #todays_date = date.today().strftime("%d/%m/%Y")
    #main()
    myUser = User.query.all()

    for user in myUser:
        print(user.email)
            #send_email("Update on reddit", f"\nGoodmorning Nazif!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)", "info.csv", user.email)
    return render_template("home.html", myUser=myUser)

@app.route("/user", methods=["POST"])
def user():
    user = User(request.form["username"], request.form["email"])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
