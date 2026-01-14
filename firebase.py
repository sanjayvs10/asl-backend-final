import firebase_admin
import json
import os
from firebase_admin import credentials, db

firebase_key = json.loads(os.environ.get("FIREBASE_KEY"))

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://asl-auction-management-system-default-rtdb.firebaseio.com/'
})

players_ref = db.reference("players")
teams_ref = db.reference("teams")
users_ref = db.reference("users")
