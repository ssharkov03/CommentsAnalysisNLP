from config import CLIENT_ID, SECRET_KEY, USERNAME, PASSWORD
import requests
import pandas as pd
from datetime import datetime

subreddit_name = input("Input topic: ")  # topic input
timeframe = int(input("Input timeframe: "))  # first seconds of search duration

# authenticate API
auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

# here we pass our login method (password), username, and password
data = {'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD}

# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': 'CollectComments/0.0.1'}

# send our request for an OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# while the token is valid (~2 hours) we just add headers=headers to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

# initialize dataframe and parameters for pulling data in loop
data = pd.DataFrame()
# get one post for one request
params = {'limit': 1}

# create dataset while valid responses
while res.status_code == 200:

    # make request
    link = f"https://oauth.reddit.com/r/{subreddit_name}/new"
    res = requests.get(f"https://oauth.reddit.com/r/{subreddit_name}/new",
                       headers=headers,
                       params=params)

    # creating dataset while in timeframe
    comment_time = datetime.fromtimestamp(res.json()['data']['children'][0]['data']['created_utc'])
    if (datetime.now() - comment_time).total_seconds() > timeframe:
        break

    # skip post if only title (without text itself) is provided
    if res.json()['data']['children'][0]['data']['selftext'] != '':
        # add new post to dataframe
        data = data.append({
            'subreddit': res.json()['data']['children'][0]['data']['subreddit'],
            'title': res.json()['data']['children'][0]['data']['title'],
            'selftext': res.json()['data']['children'][0]['data']['selftext'],
            'upvote_ratio': res.json()['data']['children'][0]['data']['upvote_ratio'],
            'ups': res.json()['data']['children'][0]['data']['ups'],
            'downs': res.json()['data']['children'][0]['data']['downs'],
            'score': res.json()['data']['children'][0]['data']['score'],
            'link_flair_css_class': res.json()['data']['children'][0]['data']['link_flair_css_class'],
            'created_utc': datetime.fromtimestamp(res.json()['data']['children'][0]['data']['created_utc']),
            # datetime!
            'id': res.json()['data']['children'][0]['data']['id'],
            'kind': res.json()['data']['children'][0]['kind']
        }, ignore_index=True)

    # take the oldest entry & create fullname
    fullname = res.json()['data']['children'][0]['kind'] + '_' + res.json()['data']['children'][0]['data']['id']
    # add/update fullname in params
    params['after'] = fullname

data.to_csv("sample_df.csv")
