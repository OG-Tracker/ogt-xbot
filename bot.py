import os
import json
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta


# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")  # Add your Bearer Token to .env
JSON_FILE_PATH = "projects.json"

# Authenticate to Twitter using API v2 Client
def authenticate_twitter_v2():
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    print("Authentication OK")
    return client

# Post a tweet using API v2
def post_tweet_v2(client, track, refNum, deadline, twitter_handle, proposer):
    handle = f"@{twitter_handle.split('/')[-1]}" if twitter_handle and twitter_handle != "-" else proposer
    if handle == "-" or not handle:
        handle = "Project team"

    tweet_content = (
        f"The deadline of REF #{refNum} will be reached in 7 days. ({deadline})\n"
        f"{handle}\n\n"
        f"View: app.ogtracker.io/{track}/{refNum}"
    )

    try:
        response = client.create_tweet(text=tweet_content)
        if response:
            print(f"Tweet posted for REF #{refNum}: {tweet_content}")
    except tweepy.errors.Forbidden as e:
        print(f"Failed to post tweet for REF #{refNum} - Forbidden: {e}")
    except Exception as e:
        print(f"Failed to post tweet for REF #{refNum} due to an unexpected error: {e}")

# Load project data from JSON file
def load_json_data(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data["data"]

# Check if a project date is 7 days from today
def is_7_days_before_date(ldate):
    try:
        current_date = datetime.now().date()
        target_date = datetime.strptime(ldate, "%Y-%m-%d").date()
        return target_date - timedelta(days=7) == current_date
    except ValueError:
        return False

# Main function to check deadlines and post tweets
def main():
    client = authenticate_twitter_v2()
    projects = load_json_data(JSON_FILE_PATH)
    for project in projects:
        refNum = project.get("refNum")
        track = project.get("track")
        ldate = project.get("ldate", "")
        twitter_handle = project.get("twitter", "")
        proposer = project.get("proposer", "")

        # Skip project if 'fdate' is "-" or missing
        if ldate == "-" or not ldate:
            continue

        # Only post tweet if today is 7 days before the fdate
        if is_7_days_before_date(ldate):
            post_tweet_v2(client, track, refNum, ldate, twitter_handle, proposer)

if __name__ == "__main__":
    main()
