from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emails.db"
app.config['SECRET_KEY'] = 'super secret key'

#Initialize
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), unique = True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "<Name %r>" % self.email

class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("submit")

@app.route("/", methods = ["POST", "GET"])
def home():
    email = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        print(user)
        if user is None:
            user = Users(email = form.email.data)
            print(user)
            db.session.add(user)
            db.session.commit()
        email = form.email.data
        print(email)
        form.email.data = ""
        flash("User added sucsessfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("index.html", form=form, email = email, our_users=our_users)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)