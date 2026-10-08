import os
import time

import psycopg
from flask import Flask, jsonify, request
from psycopg.rows import dict_row

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://cloudtask:cloudtask@postgres:5432/cloudtask",
)


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def initialize_database():
    for attempt in range(15):
        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        completed BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            return
        except psycopg.OperationalError:
            if attempt == 14:
                raise
            time.sleep(2)


initialize_database()


@app.get("/health")
def health():
    return jsonify(status="healthy"), 200


@app.get("/ready")
def ready():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
        return jsonify(status="ready"), 200
    except psycopg.Error:
        return jsonify(status="not ready"), 503


@app.get("/api/tasks")
def list_tasks():
    with get_connection() as connection:
        tasks = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks ORDER BY id"
        ).fetchall()
    return jsonify(tasks), 200


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()

    if not title:
        return jsonify(error="Task title is required"), 400

    with get_connection() as connection:
        task = connection.execute(
            """
            INSERT INTO tasks (title)
            VALUES (%s)
            RETURNING id, title, completed, created_at
            """,
            (title,),
        ).fetchone()

    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    completed = bool(data.get("completed", False))

    with get_connection() as connection:
        task = connection.execute(
            """
            UPDATE tasks
            SET completed = %s
            WHERE id = %s
            RETURNING id, title, completed, created_at
            """,
            (completed, task_id),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found"), 404

    return jsonify(task), 200


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with get_connection() as connection:
        task = connection.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id",
            (task_id,),
        ).fetchone()

    if task is None:
        return jsonify(error="Task not found"), 404

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)