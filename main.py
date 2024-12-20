import os
import base64
import hashlib
import re
import json
from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://127.0.0.1:5000/oauth/callback"

# Allow OAuth 2.0 to work with HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# OAuth 2.0 URLs and settings
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
scopes = ["tweet.read", "tweet.write", "offline.access"]

# PKCE setup
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def demo():
    try:
        print("Starting OAuth flow...")
        twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        authorization_url, state = twitter.authorization_url(
            auth_url, code_challenge=code_challenge, code_challenge_method="S256"
        )
        session["oauth_state"] = state
        print("Redirecting to Twitter for authorization.")
        return redirect(authorization_url)
    except Exception as e:
        print("Error during OAuth flow initiation:", e)
        return "An error occurred during the OAuth flow initiation."

@app.route("/oauth/callback", methods=["GET"])
def callback():
    try:
        twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        token = twitter.fetch_token(
            token_url,
            client_secret=client_secret,
            code_verifier=code_verifier,
            authorization_response=request.url,
        )
        
        # Log the token for debugging
        print("Token retrieved:", token)

        # Check if the token retrieval was successful before saving
        if "access_token" in token:
            with open("tokens.json", "w") as f:
                json.dump(token, f)
            print("Tokens successfully saved in tokens.json")
            return "Authorization successful! Tokens saved."
        else:
            print("Failed to retrieve access token.")
            return "Failed to retrieve access token."

    except Exception as e:
        print("Error during OAuth callback:", e)
        return "An error occurred during the OAuth callback."

if __name__ == "__main__":
    app.run(port=5000)
