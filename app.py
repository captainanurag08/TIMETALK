from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import datetime
import os

# Corrected 'name' to '__name__'
app = Flask(__name__)
DB = "tasks.db"

# -----------------------------
# DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        day TEXT,
        start TEXT,
        end TEXT,
        priority TEXT
    )
    ''')
    conn.commit()
    conn.close()

# -----------------------------
# DATABASE HELPERS
# -----------------------------
def get_tasks():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return rows

def tasks_by_day(day):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute(
        "SELECT * FROM tasks WHERE day=? ORDER BY start",
        (day,)
    ).fetchall()
    conn.close()
    return rows

def add_task(title, day, start, end, priority="Medium"):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks(title,day,start,end,priority) VALUES(?,?,?,?,?)",
        (title, day, start, end, priority)
    )
    conn.commit()
    conn.close()

def delete_task(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    today = datetime.datetime.today().strftime("%A")
    tasks = tasks_by_day(today)
    return render_template("home.html", tasks=tasks, today=today)

@app.route("/schedule")
def schedule():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    data = {d: tasks_by_day(d) for d in days}
    return render_template("schedule.html", data=data)

# -----------------------------
# ADD / DELETE TASK
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        add_task(
            request.form["title"],
            request.form["day"],
            request.form["start"],
            request.form["end"],
            request.form.get("priority", "Medium")
        )
        return redirect("/schedule")
    return render_template("add.html")

# Added <id> parameter to the route
@app.route("/delete/<int:id>")
def delete(id):
    delete_task(id)
    return redirect("/schedule")

# -----------------------------
# SEARCH / TIME UTILS
# -----------------------------
@app.route("/search")
def search_page():
    return render_template("search.html")

def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def minutes_to_time(m):
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

# -----------------------------
# SLOT FINDER (MULTIPLE SLOTS)
# -----------------------------
@app.route("/find_slot", methods=["POST"])
def find_slot():
    data = request.json
    day = data["day"]
    duration = int(data["duration"])
    start_range = time_to_minutes(data["start"])
    end_range = time_to_minutes(data["end"])

    tasks = tasks_by_day(day)
    blocks = [(time_to_minutes(t[3]), time_to_minutes(t[4])) for t in tasks]
    blocks.sort()

    slots = []
    current = start_range

    for s, e in blocks:
        if s >= end_range:
            break
        if s - current >= duration:
            slots.append({
                "start": minutes_to_time(current),
                "end": minutes_to_time(current + duration)
            })
            if len(slots) >= 5:
                break
        current = max(current, e)

    if end_range - current >= duration and len(slots) < 5:
        slots.append({
            "start": minutes_to_time(current),
            "end": minutes_to_time(current + duration)
        })

    if not slots:
        return jsonify({"error": "No free slot in this time range"})
    return jsonify(slots)

# -----------------------------
# WEEKLY / AUTO SCHEDULING
# -----------------------------
@app.route("/add_auto", methods=["POST"])
def add_auto():
    data = request.json
    add_task(
        data["title"], data["day"], data["start"], 
        data["end"], data.get("priority", "Medium")
    )
    return jsonify({"status": "ok"})

@app.route("/weekly_auto", methods=["POST"])
def weekly_auto():
    data = request.json
    title = data["title"]
    duration = int(data["duration"])
    priority = data.get("priority", "Medium")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for d in days:
        tasks = tasks_by_day(d)
        blocks = [(time_to_minutes(t[3]), time_to_minutes(t[4])) for t in tasks]
        blocks.sort()

        start_day, end_day = 6 * 60, 22 * 60
        current = start_day
        placed = False

        for s, e in blocks:
            if s - current >= duration:
                add_task(title, d, minutes_to_time(current), minutes_to_time(current + duration), priority)
                placed = True
                break
            current = max(current, e)

        if not placed and (end_day - current >= duration):
            add_task(title, d, minutes_to_time(current), minutes_to_time(current + duration), priority)

    return jsonify({"status": "done"})

# -----------------------------
# NOTIFICATIONS / FOCUS
# -----------------------------
@app.route("/tasks_today")
def tasks_today():
    today = datetime.datetime.today().strftime("%A")
    tasks = tasks_by_day(today)
    result = [{"title": t[1], "start": t[3], "priority": t[5]} for t in tasks]
    return jsonify(result)
@app.route("/manual-weekly", methods=["POST"])
def manual_weekly():

    data = request.json

    title = data["title"]
    day = data["day"]
    start = data["start"]
    end = data["end"]
    priority = data["priority"]

    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO tasks(title,day,start,end,priority)
    VALUES(?,?,?,?,?)
    """,(title,day,start,end,priority))

    conn.commit()
    conn.close()

    return {"status":"ok"}

@app.route("/focus")
def focus():
    return render_template("focus.html")

# Corrected 'name' to '__name__' and 'main' to '__main__'
if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)