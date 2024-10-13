import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import os
from config import Config
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from flask_flatpages import FlatPages
from data import items

ENV_FILE = find_dotenv() # finds the env and loads credentials!! Woohoo
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = env.get("APP_SECRET_KEY") # configuring flask for my app via the generated key.

flatpages = FlatPages(app)

oauth = OAuth(app)

oauth.register( # Configure OAuth
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET","POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session['user'] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.before_request
def before_request():
    if 'progress' not in session:
        session['progress'] = {item['id']: {'learned': False, 'proficient': False} for item in items}

@app.route('/', methods =['POST','GET'])
def home():
    if request.method == 'POST':
        for item in items:
            item_id = item['id']
            learned = request.form.get(f'learned_{item_id}') == 'on'
            proficient = request.form.get(f'proficient_{item_id}') == 'on'
            session['progress'][item_id]['learned'] = learned
            session['progress'][item_id]['proficient'] = proficient
        
        session.modified = True
        return redirect(url_for('home'))
    total_items = len(items)
    learned_count = sum(1 for progress in session['progress'].values() if progress['learned'])
    proficient_count = sum(1 for progress in session['progress'].values() if progress['proficient'])
    learned_progress = (learned_count / total_items) * 100 if total_items > 0 else 0
    proficient_progress = (proficient_count / total_items) * 100 if total_items > 0 else 0

    return render_template('classes.html',
                           items=items,
                           progress=session['progress'],
                           learned_progress=learned_progress,
                           proficient_progress=proficient_progress,
                           total_items=total_items)


# @app.route("/")
# def home():
#     return render_template("classes.html", items=items, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)
