import requests
import pandas as pd
from datetime import date, datetime, time
import logging
from requests.auth import HTTPBasicAuth
from send_mail import send_email
from pymongo import MongoClient
from config import CLIENT_ID, SECRET_KEY, pw
import schedule

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
    # Schedule the send_emails function to run every day at 8:00 AM
    schedule.every().day.at("8:00").do(send_emails)

def send_emails():
    # Connect to the MongoDB server and select the database and collection
    client = MongoClient('mongodb://NazifTheDon:Aareyuok.123@localhost:5000/emails')
    db = client['emails']
    collection = db['emails']

    # Get a list of all emails in the database
    emails = collection.find()

    # Retrieve posts about Tesla from the subreddit r/wallstreetbets/new
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
            if(" tesla " in description_lower or " tesla " in title_lower or ("tesla ") in title_lower ):
                posts.append({
                    "Title" : data_of["title"],
                    "Abbreddit" : data_of["subreddit"],
                    "Author": data_of["author"],
                                    "Content": (data_of["selftext"] if(data_of["selftext"]) else "No Description"),
                    "Link": data_of["url"]
                    })
        if not posts:
            break
        df = df.append(posts, ignore_index=True)
        after = res.json()["data"]["after"]
    if df.empty:
        logger.info("No posts about Tesla found.")
        return
    # Convert the DataFrame to a CSV file
    csv = df.to_csv(index=False)
    # Send the email with the CSV file to each email in the list
    todays_date = date.today().strftime("%d/%m/%Y")
    subject = "Update on reddit"
    message = f"\nGoodmorning Nazif!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)"
    for email in emails:
        send_email(subject, message, "info.csv", email, attachments=[("info.csv", "text/csv", csv)])

def getInfo(link, df):
    res = requests.get(f"https://oauth.reddit.com/{link}",
                 headers=headers, params={"limit": "100"})
    for post in res.json()["data"]["children"]:
        data_of = post["data"]
        description_lower = data_of["selftext"].lower()
        title_lower = data_of["title"].lower()
        if(" tesla " in description_lower or " tesla " in title_lower or ("tesla ") in title_lower ):
            df = df.append({
                "Title" : data_of["title"],
                "Abbreddit" : data_of["subreddit"],
                "Author": data_of["author"],
                "Content": (data_of["selftext"] if(data_of["selftext"]) else "No Description"),
                "Link": data_of["url"]
                }, ignore_index = True)
    csv = df.to_csv
    return csv


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    try:
        main()
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logger.exception("An error occurred:")
