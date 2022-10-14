import requests
import pandas as pd
from datetime import date, datetime
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


def main():
    df = pd.DataFrame()
    #todays_date = date.today().strftime("%d/%m/%Y")
    getInfo("r/wallstreetbets/new", df)
    #send_email("Update on reddit", f"\nGoodmorning Nazif!\nHere is the daily update.\nTodays date is: {todays_date} \n\n- From CertifiedSideBoi (Reddit)", "info.csv")


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
    df = df.to_csv("info.csv", index=False, sep=";")
    return df


if __name__ == '__main__':
    main()



