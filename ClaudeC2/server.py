from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "tasks.db"

# --- Initialize DB ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            output TEXT
        )
        """)
        conn.commit()

# --- Add task ---
@app.route("/create_task", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Missing 'command' field"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (command, status) VALUES (?, 'Pending')", (data["command"],))
        conn.commit()
        task_id = cursor.lastrowid

    return jsonify({"message": "Task created", "id": task_id})

#Get all pending tasks ---
@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, command FROM tasks WHERE status = 'Pending'")
        tasks = [{"id": row[0], "command": row[1]} for row in cursor.fetchall()]
    return jsonify({"tasks": tasks})

@app.route("/get_tasks_status", methods=["GET"])
def get_tasks_status():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, command, status, output FROM tasks")
        tasks = [
            {"id": row[0], "command": row[1], "status": row[2], "output": row[3] or ""}
            for row in cursor.fetchall()
        ]
    return jsonify({"tasks": tasks})


# Add results to DB
@app.route("/submit_result", methods=["POST"])
def submit_result():
    data = request.get_json()
    if not data or "id" not in data or "output" not in data:
        return jsonify({"error": "Missing 'id' or 'output'"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'Completed', output = ? WHERE id = ?", (data["output"], data["id"]))
        conn.commit()

    return jsonify({"message": "Result submitted successfully"})

if __name__ == "__main__":
    init_db()
    app.run("0.0.0.0", port=8080)
