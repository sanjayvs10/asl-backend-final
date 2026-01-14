from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from firebase import players_ref, teams_ref, users_ref
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add Player
@app.route("/add-player", methods=["POST"])
def add_player():
    data = request.json
    players_ref.push(data)
    return jsonify({"msg":"Player added"})

# Add Team
@app.route("/add-team", methods=["POST"])
def add_team():
    data = request.json
    data["remainingBudget"] = data["totalBudget"]
    teams_ref.push(data)
    return jsonify({"msg":"Team added"})

# Sell Player
@app.route("/sell-player", methods=["POST"])
def sell_player():
    data = request.json
    print("RECEIVED:", data)
    player_id = data["playerId"]
    team_id = data["teamId"]
    price = int(data["price"])

    team = teams_ref.child(team_id).get()
    new_balance = team["remainingBudget"] - price

    teams_ref.child(team_id).update({
        "remainingBudget": new_balance
    })

    players_ref.child(player_id).update({
        "soldTo": team_id,
        "soldPrice": price
    })

    return jsonify({"msg":"Player sold successfully"})

# Create Admin (run once)
@app.route("/create-admin")
def create_admin():
    users_ref.child("admin").set({
        "username":"ADMIN",
        "password": generate_password_hash("admin123")
    })
    return "Admin created"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data["role"]
    name = data["name"]
    password = data["password"]

    # ADMIN LOGIN
    if role == "admin":
        admin = users_ref.child("admin").get()
        if admin and admin["username"] == name and \
           check_password_hash(admin["password"], password):
            return jsonify({"msg":"success","role":"admin"})

    # MANAGER LOGIN
    else:
        managers = users_ref.child("managers").get()

        if not managers:   # 👈 SAFETY CHECK
            return jsonify({"msg":"invalid"})

        for mid in managers:
            if managers[mid]["name"] == name:
                if check_password_hash(managers[mid]["password"], password):
                    return jsonify({
                        "msg":"success",
                        "role":"manager",
                        "teamId": managers[mid]["teamId"]
                    })

    return jsonify({"msg":"invalid"})

@app.route("/add-manager", methods=["POST"])
def add_manager():
    data = request.json

    team_data = {
        "teamName": data["teamName"],
        "logo": data["logo"],
        "manager1": data["manager1"],
        "manager2": data["manager2"],
        "phone": data["phone"],
        "totalBudget": 500000,
        "remainingBudget": 500000
    }

    # save team
    team_ref = teams_ref.push(team_data)

    # save manager login
    users_ref.child("managers").push({
        "name": data["manager1"],   # username
        "password": generate_password_hash(data["password"]),
        "teamId": team_ref.key
    })

    return jsonify({"msg":"Manager added"})


@app.route("/get-players")
def get_players():
    return players_ref.get()

@app.route("/get-teams")
def get_teams():
    return teams_ref.get()

@app.route("/get-team/<team_id>")
def get_team(team_id):

    team = teams_ref.child(team_id).get()

    print("TEAM FROM DB:", team)  # debug

    if not team:
        return jsonify({})

    return jsonify(team)


# Get players of one team
@app.route("/get-team-players/<team_id>")
def get_team_players(team_id):
    players = players_ref.get()
    result = {}

    for pid in players:
        if players[pid].get("soldTo") == team_id:
            result[pid] = players[pid]

    return jsonify(result)

# All players with status
@app.route("/admin-players")
def admin_players():
    players = players_ref.get()
    teams = teams_ref.get()

    result = []

    for pid in players:
        p = players[pid]
        teamName = "-"

        if p.get("soldTo"):
            teamName = teams[p["soldTo"]]["teamName"]

        result.append({
            "name": p["name"],
            "category": p["category"],
            "position": p.get("position","-"),   # 👈 NEW
            "status": "SOLD" if p.get("soldTo") else "UNSOLD",
            "team": teamName,
            "price": p.get("soldPrice", "-")
        })

    return jsonify(result)


# All teams standings
@app.route("/admin-teams")
def admin_teams():
    teams = teams_ref.get()
    players = players_ref.get()

    result = []

    for tid in teams:
        team = teams[tid]
        taken = []

        for pid in players:
            if players[pid].get("soldTo") == tid:
                taken.append(players[pid]["name"])

        result.append({
            "team": team["teamName"],
            "managers": team["manager1"] + " & " + team["manager2"],
            "players": taken,
            "remaining": team["remainingBudget"]
        })

    return jsonify(result)




# 🚀 KEEP THIS ALWAYS AT BOTTOM
app.run(debug=True)
