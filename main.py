import requests
import pandas as pd
from datetime import date
from requests.auth import HTTPBasicAuth
from send_mail import send_email


CLIENT_ID = '_WuqZxzKBaOX7_5_PjP91g'
SECRET_KEY = 'fUZByulvvO1zKHihOUfGxpQs1GEreg'
auth = HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
with open('pw', 'r') as f:
    pw = f.read()

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

df = pd.DataFrame()

def getInfo(link, df):
    res = requests.get(f"https://oauth.reddit.com/{link}",
                 headers=headers, params={"limit": "100"})
    for post in res.json()["data"]["children"]:
        dataOf = post["data"]
        descriptionLower = dataOf["selftext"].lower()
        if(" tesla " in descriptionLower):
            df = df.append({
                "Title" : dataOf["title"],
                "Abbreddit" : dataOf["subreddit"],
                "Author": dataOf["author"],
                "Content": (dataOf["selftext"] if(dataOf["selftext"]) else "No Description"),
                "Link": dataOf["url"]
                }, ignore_index = True)
    df = df.to_csv("test.csv", index=False, sep=";")
    return df


todays_date = "\033[1m" + date.today().strftime("%d/%m/%Y") + "\033[0m"


send_email(f"Update on reddit", f"\nGoodmorning Nazif!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)")


