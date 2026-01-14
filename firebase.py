import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://asl-auction-management-system-default-rtdb.firebaseio.com/'
})

players_ref = db.reference("players")
teams_ref = db.reference("teams")
users_ref = db.reference("users")
