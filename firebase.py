import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase key from ENV variable
firebase_key = json.loads(os.environ.get("FIREBASE_KEY"))

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

db = firestore.client()

players_ref = db.collection("players")
teams_ref = db.collection("teams")
users_ref = db.collection("users")
