\
import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database connection details - fetched from environment variables
DB_NAME = os.getenv("DB_NAME", "match_scores")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "") # Default to empty if not set
DB_HOST = os.getenv("DB_HOST", "localhost") # Default to localhost if not set
DB_PORT = os.getenv("DB_PORT", "5432") # Default PG port

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        # In a real app, you might want more robust error handling
        # or retry logic here.
        return None

@app.route('/api/matches', methods=['POST'])
def add_match():
    """
    API endpoint to receive and store match results.
    Expects JSON data like:
    {
        "player1_name": "Alice",
        "player2_name": "Bob",
        "player1_score": 10,
        "player2_score": 5
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Basic validation
    required_fields = ["player1_name", "player2_name", "player1_score", "player2_score"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    player1_name = data['player1_name']
    player2_name = data['player2_name']
    player1_score = data['player1_score']
    player2_score = data['player2_score']

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()
    try:
        # The match_datetime is handled by the database DEFAULT
        cur.execute(
            """
            INSERT INTO matches (player1_name, player2_name, player1_score, player2_score)
            VALUES (%s, %s, %s, %s)
            RETURNING id, match_datetime;
            """,
            (player1_name, player2_name, player1_score, player2_score)
        )
        new_match_id, match_time = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "message": "Match added successfully",
            "match_id": new_match_id,
            "match_time": match_time.isoformat() # Format timestamp nicely
        }), 201
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting data: {error}")
        if conn:
            conn.rollback() # Roll back the transaction on error
            cur.close()
            conn.close()
        return jsonify({"error": "Failed to add match to database"}), 500


# Basic route to check if the server is running
@app.route('/')
def index():
    return "Flask Match Score Backend is running!"

if __name__ == '__main__':
    # Run the app. 'debug=True' is helpful for development.
    # Use 'host=0.0.0.0' to make it accessible on your network.
    app.run(host='0.0.0.0', port=5000, debug=True)
