import requests
import pandas as pd
from datetime import date, time
import logging
from requests.auth import HTTPBasicAuth
from send_mail import send_email
from config import CLIENT_ID, SECRET_KEY, pw_database, pw
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler

auth = HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

data = {
    "grant_type": "password",
    "username": "CertifiedSideBoi",
    "password": pw
}
headers = {"User-Agent": "MyAPI/0.0.1"}
res = requests.post("https://www.reddit.com/api/v1/access_token",
                    auth = auth,
                    data = data,
                    headers = headers)
TOKEN = res.json()['access_token']
headers["Authorization"] = f'bearer {TOKEN}'

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Create a background scheduler
    scheduler = BackgroundScheduler()

    # Schedule the send_emails function to run every day at 8:00 AM
    scheduler.add_job(send_emails, 'cron', hour=19, minute=59, timezone='US/Pacific')

    # Start the scheduler
    scheduler.start()
def send_emails():
    # Connect to the MySQL database
    cnx = mysql.connector.connect(user='root', password=pw_database, host='localhost', database='emails')

    # Create a cursor object
    cursor = cnx.cursor()

    # Retrieve all emails from the emails table
    sql = 'SELECT email FROM emails'
    cursor.execute(sql)
    rows = cursor.fetchall()
    emails = [row[0] for row in rows]
    print("working")
    # Retrieve posts about Tesla from the subreddit r/wallstreetbets/new
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
                "Content": content
            })

    df = df.append(posts, ignore_index=True)

    # Process the data and send the email
    # Convert the DataFrame to a CSV file
    csv = df.to_csv("info.csv", index=False)
    # Send the email with the CSV file to each email in the list
    todays_date = date.today().strftime("%d/%m/%Y")
    subject = "Update on reddit"
    message = f"\nGoodmorning!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)"
    for email in emails:
        send_email(subject, message, "info.csv", email, attachments=[("info.csv", "text/csv", csv)])

    # Close the cursor and connection to the database
    cursor.close()
    cnx.close()


if __name__ == '__main__':
    main()