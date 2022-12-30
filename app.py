from config import pw_database
import re
from main import headers
from send_mail import send_email
import pandas as pd
import requests
import mysql.connector
from flask import Flask, request, render_template

app = Flask(__name__)
# Define the route for the index page
@app.route('/')
def index():
    return render_template('index.html')


# Define the route for handling form submissions from the index page
@app.route('/submit', methods=['POST'])
def submit():
    # Check if the email field is present in the form submission
    if 'email' in request.form:
        # Get the email from the form submission
        email = request.form['email']
        cnx = mysql.connector.connect(user='root', password=pw_database, host='localhost', database='emails')

        # Create a cursor object
        cursor = cnx.cursor()

        # Define the pattern for matching email addresses
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Check if the email matches the pattern
        if re.match(pattern, email):
            # Check if the email is already in the database
            sql = 'SELECT email FROM emails WHERE email = %s'
            val = (email,)
            cursor.execute(sql, val)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            if len(rows) > 0:
                # Email is already in the database
                cursor.close()
                cnx.close()
                return 'You are already subscribed!'
            else:
                # Save the email to the MySQL database
                sql = 'INSERT INTO emails (email) VALUES (%s)'
                cursor.execute(sql, val)
                cnx.commit()
                cursor.close()
                cnx.close()
                return 'Email saved successfully'
        else:
            # Return an error if the email is not a valid email address
            return 'Error: not a valid email'
    else:
        # Return an error if the email field is not found
        return 'Error: email field not found in form submission'

# Define the route for the base page
@app.route('/base.html')
def base():
    return render_template('base.html')


# Define the route for handling form submissions from the base page
@app.route('/submit_now', methods=['POST'])
def send_email_now():
    email = request.form['email']
    df = pd.DataFrame()
    link = "r/wallstreetbets/top?sort=new&t=day&limit=100"
    # Make an API call to retrieve the top 100 posts
    res = requests.get(f"https://oauth.reddit.com/{link}", headers=headers)
    # Append the relevant information about the posts to the DataFrame
    posts = []
    for post in res.json()["data"]["children"]:
        data_of = post["data"]
        description_lower = data_of["selftext"].lower()
        title_lower = data_of["title"].lower()
        if "tesla" in description_lower or "tesla" in title_lower:
            content = data_of["selftext"].replace("&amp;#x200B;", "")
            posts.append({
                "Title": data_of["title"],
                "Subreddit": data_of["subreddit"],
                "Author": data_of["author"],
                "Content":  content
            })

    df = df.append(posts, ignore_index=True)
    # Process the data and send the email
    send(email, df)
    return 'Email sent successfully'

# Define the route for the unsubscribe page
@app.route('/unsubscribe.html')
def unsubscribe():
    return render_template('unsubscribe.html')

# Define the route for handling form submissions from the unsubscribe page
@app.route('/unsubscribe', methods=['POST'])
def remove_email():
    # Check if the email field is present in the form submission
    if 'email' in request.form:
        # Get the email from the form submission
        email = request.form['email']

        # Connect to the MySQL database
        cnx = mysql.connector.connect(user='root', password=pw_database, host='localhost', database='emails')

        # Create a cursor object
        cursor = cnx.cursor()

        # Define the DELETE query
        sql = 'DELETE FROM emails WHERE email = %s'
        val = (email,)

        # Execute the DELETE query
        cursor.execute(sql, val)
        cnx.commit()

        # Check if the email was deleted
        cursor.execute(sql, val)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        if len(rows) == 0:
            # Email was deleted
            cursor.close()
            cnx.close()
            return 'Email removed successfully'
        else:
            # Email was not deleted
            cursor.close()
            cnx.close()
            return 'Error: email not found in database'
    else:
        # Return an error if the email field is not found
        return 'Error: email field not found in form submission'

def send(email, df):
    df.to_csv("info.csv", index=False, encoding='utf-8')  # Save the data in df to a CSV file
    subject = "Tesla updates"
    body = f"Here are the latest Tesla updates:"
    file = "info.csv"  # Attach the CSV file
    attachments = None
    send_email(subject, body, file, email, attachments)


if __name__ == '__main__':
    app.run(debug=True)

