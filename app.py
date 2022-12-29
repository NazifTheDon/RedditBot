from datetime import date

from flask import Flask, request, render_template
from pymongo import MongoClient
import re
from main import getInfo, headers
import pandas as pd
import requests
import logging


app = Flask(__name__)

# Connect to the MongoDB server
client = MongoClient('mongodb://NazifTheDon:Aareyuok.123@localhost:5000/emails')

# Select the database and collection to use
db = client['emails']
collection = db['emails']


@app.route('/')
def index():
    return render_template('index.html')

# Define the route for handling form submissions
import re

@app.route('/submit', methods=['POST'])
def submit():
    # Check if the email field is present in the form submission
    if 'email' in request.form:
        # Get the email from the form submission
        email = request.form['email']

        # Define the pattern for matching email addresses
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Check if the email matches the pattern
        if re.match(pattern, email):
            # Save the email to the database
            collection.insert_one({'email': email})
            return 'Email saved successfully'
        else:
            # Return an error if the email is not a valid email address
            return 'Error: not a valid email'
    else:
        # Return an error if the email field is not found
        return 'Error: email field not found in form submission'

@app.route('/base.html')
def base():
    return render_template('base.html')

@app.route('/submit_now', methods=['POST'])
def send_email():
    email = request.form['email']
    df = pd.DataFrame()
    link = "r/wallstreetbets/new"
    after = None
    while True:
        # Make an API call to retrieve a page of results
        params = {"limit": "100"}
        if after:
            params["after"] = after
        res = requests.get(f"https://oauth.reddit.com/{link}",
                           headers=headers, params=params)
        # Append the relevant information about the posts to the DataFrame
        posts = []
        for post in res.json()["data"]["children"]:
            data_of = post["data"]
            description_lower = data_of["selftext"].lower()
            title_lower = data_of["title"].lower()
            if (" tesla " in description_lower or " tesla " in title_lower or ("tesla ") in title_lower):
                posts.append({
                    "Title": data_of["title"],
                    "Abbreddit": data_of["subreddit"],
                    "Author": data_of["author"],
                    "Content": (data_of["selftext"] if (data_of["selftext"]) else "No Description"),
                    "Link": data_of["url"]
                })
        if not posts:
            break
        df = df.append(posts, ignore_index=True)
        after = res.json()["data"]["after"]
    if df.empty:
        return 'There are currently no post in that thread about Tesla :('
    # Convert the DataFrame to a CSV file
    csv = df.to_csv(index=False)
    # Send the email with the CSV file to each email in the list
    todays_date = date.today().strftime("%d/%m/%Y")
    subject = "Update on reddit"
    message = f"\nGoodmorning Nazif!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)"
    send_email(subject, message, "info.csv", email, attachments=[("info.csv", "text/csv", csv)])
    return "Email sent!"


if __name__ == '__main__':
    app.run(debug=True)
