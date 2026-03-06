from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS players(
id SERIAL PRIMARY KEY,
name TEXT UNIQUE,
country TEXT,
role TEXT,
runs INT,
wickets INT,
base_price INT,
current_price INT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bids(
id SERIAL PRIMARY KEY,
player_id INT,
bid_price INT,
bid_time TIMESTAMP
);
""")

conn.commit()

# insert players
cur.execute("""
INSERT INTO players(name,country,role,runs,wickets,base_price,current_price)
VALUES
('Virat Kohli','India','Batsman',7263,4,20000000,20000000),
('Rohit Sharma','India','Batsman',6200,15,20000000,20000000),
('Jasprit Bumrah','India','Bowler',50,145,15000000,15000000),
('KL Rahul','India','Batsman',4200,0,18000000,18000000),
('Jos Buttler','England','Batsman',3500,0,15000000,15000000),
('Rashid Khan','Afghanistan','Bowler',500,130,15000000,15000000)
ON CONFLICT (name) DO NOTHING;
""")

conn.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/players")
def players():

    cur.execute("SELECT * FROM players")
    data = cur.fetchall()

    players = []

    for p in data:
        players.append({
            "id":p[0],
            "name":p[1],
            "country":p[2],
            "role":p[3],
            "runs":p[4],
            "wickets":p[5],
            "price":p[7]
        })

    return jsonify(players)

@app.route("/bid", methods=["POST"])
def bid():

    player_id = request.json["player_id"]
    bid_price = int(request.json["price"])

    cur.execute(
        "SELECT current_price FROM players WHERE id=%s",
        (player_id,)
    )

    current = cur.fetchone()[0]

    if bid_price <= current:
        return jsonify({"status":"Bid too low"})

    cur.execute(
        "UPDATE players SET current_price=%s WHERE id=%s",
        (bid_price,player_id)
    )

    cur.execute(
        "INSERT INTO bids(player_id,bid_price,bid_time) VALUES(%s,%s,%s)",
        (player_id,bid_price,datetime.now())
    )

    conn.commit()

    return jsonify({"status":"Bid accepted"})

if __name__ == "__main__":
    app.run()
