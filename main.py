import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

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
        df = df.append({
            "title" : dataOf["title"],
            "subbreddit" : dataOf["subreddit"],
            "author": dataOf["author"],
            "Content": (dataOf["selftext"] if(dataOf["selftext"]) else "No Description"),
            }, ignore_index = True)
    #print(post["data"].keys())
    df = df.to_csv("test.csv", index=False, sep=";")
    return df

print(getInfo("/r/python/new", df))


