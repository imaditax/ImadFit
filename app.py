from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "fitlog_super_secret"
@app.context_processor
def inject_user():

    if "user_id" in session:

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        db.close()


        return dict(
            logged_in=True,
            current_user=user
        )


    return dict(
        logged_in=False,
        current_user=None
    )

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return "Must provide username"

        if not password:
            return "Must provide password"

        if password != confirmation:
            return "Passwords do not match"

        password_hash = generate_password_hash(password)

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user:
            db.close()
            return "Username already exists"

        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )

        db.commit()

        db.close()


        return "Account created!"

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")


        if not username or not password:
            return "Missing information"


        db = get_db()


        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()


        db.close()


        if user is None:
            return "User does not exist"


        if not check_password_hash(user["password_hash"], password):
            return "Wrong password"


        session["user_id"] = user["id"]


        return redirect("/")


    else:

        return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("profile.html")

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    db.close()

    if user["is_admin"] != 1:
        return "You are not authorized to access this page.", 403



    return render_template("admin.html")

@app.route("/admin/add-exercise", methods=["POST"])
def add_exercise():

    if "user_id" not in session:
        return redirect("/login")


    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()


    if user["is_admin"] != 1:
        db.close()
        return "You are not authorized to do this.", 403


    name = request.form.get("name")
    muscles = request.form.get("muscles")
    equipment = request.form.get("equipment")
    description = request.form.get("description")
    video_url = request.form.get("video_url")


    if not name or not muscles:
        db.close()
        return "Exercise name and muscles are required.", 400


    db.execute(
        """
        INSERT INTO exercises
        (name, muscles, equipment, description, video_url)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, muscles, equipment, description, video_url)
    )


    db.commit()
    db.close()


    return redirect("/admin")

@app.route("/exercises")
def exercises():

    search = request.args.get("search", "")

    db = get_db()

    if search:
        exercises = db.execute(
            """
            SELECT * FROM exercises
            WHERE name LIKE ?
            ORDER BY name
            """,
            ("%" + search + "%",)
        ).fetchall()

    else:
        exercises = db.execute(
            "SELECT * FROM exercises ORDER BY name"
        ).fetchall()

    db.close()

    return render_template(
        "exercises.html",
        exercises=exercises,
        search=search
    )
@app.route("/exercise/<int:exercise_id>")
def exercise(exercise_id):

    db = get_db()

    exercise = db.execute(
        "SELECT * FROM exercises WHERE id = ?",
        (exercise_id,)
    ).fetchone()

    db.close()


    if exercise is None:
        return "Exercise not found", 404


    return render_template(
        "exercise.html",
        exercise=exercise
    )

@app.route("/workouts")
def workouts():

    if "user_id" not in session:
        return redirect("/login")


    db = get_db()

    workouts = db.execute(
        """
        SELECT *
        FROM workouts
        WHERE user_id = ?
        ORDER BY date DESC
        """,
        (session["user_id"],)
    ).fetchall()

    db.close()


    return render_template(
        "workouts.html",
        workouts=workouts
    )

@app.route("/workout/new", methods=["GET", "POST"])
def new_workout():

    if "user_id" not in session:
        return redirect("/login")


    if request.method == "POST":

        date = request.form.get("date")
        workout_type = request.form.get("type")


        if not date or not workout_type:
            return "Missing workout information", 400


        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO workouts (user_id, date, type)
            VALUES (?, ?, ?)
            """,
            (session["user_id"], date, workout_type)
        )


        db.commit()


        workout_id = cursor.lastrowid

        db.close()


        return redirect(f"/workout/{workout_id}")


    return render_template("new_workout.html")

@app.route("/workout/<int:workout_id>")
def workout(workout_id):

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    workout = db.execute(
        """
        SELECT *
        FROM workouts
        WHERE id = ? AND user_id = ?
        """,
        (workout_id, session["user_id"])
    ).fetchone()

    if workout is None:
        db.close()
        return "Workout not found", 404

    exercises = db.execute(
        """
        SELECT *
        FROM exercises
        ORDER BY name
        """
    ).fetchall()

    sets = db.execute(
        """
        SELECT
            workout_sets.*,
            exercises.name AS exercise_name
        FROM workout_sets
        JOIN exercises
            ON workout_sets.exercise_id = exercises.id
        WHERE workout_sets.workout_id = ?
        ORDER BY exercises.name, workout_sets.set_number
        """,
        (workout_id,)
    ).fetchall()

    db.close()

    return render_template(
        "workout.html",
        workout=workout,
        exercises=exercises,
        sets=sets
    )

@app.route("/workout/<int:workout_id>/save", methods=["POST"])
def save_workout_set(workout_id):

    if "user_id" not in session:
        return redirect("/login")


    exercise_id = request.form.get("exercise_id")
    reps = request.form.get("reps")
    weight = request.form.get("weight")


    if not exercise_id or not reps or not weight:
        return "Missing workout information", 400


    db = get_db()


    # Make sure this workout belongs to the logged-in user
    workout = db.execute(
        """
        SELECT *
        FROM workouts
        WHERE id = ? AND user_id = ?
        """,
        (workout_id, session["user_id"])
    ).fetchone()


    if workout is None:

        db.close()

        return "Workout not found", 404


    # Find the next set number
    result = db.execute(
        """
        SELECT MAX(set_number)
        FROM workout_sets
        WHERE workout_id = ? AND exercise_id = ?
        """,
        (workout_id, exercise_id)
    ).fetchone()


    if result[0] is None:
        set_number = 1
    else:
        set_number = result[0] + 1


    db.execute(
        """
        INSERT INTO workout_sets
        (workout_id, exercise_id, set_number, reps, weight)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            workout_id,
            exercise_id,
            set_number,
            reps,
            weight
        )
    )


    db.commit()
    db.close()


    return redirect(f"/workout/{workout_id}")

@app.route("/set/<int:set_id>/delete", methods=["POST"])
def delete_set(set_id):

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    workout_set = db.execute(
        """
        SELECT workout_sets.id
        FROM workout_sets
        JOIN workouts
            ON workout_sets.workout_id = workouts.id
        WHERE workout_sets.id = ?
        AND workouts.user_id = ?
        """,
        (set_id, session["user_id"])
    ).fetchone()

    if workout_set is None:
        db.close()
        return "Set not found", 404

    db.execute(
        """
        DELETE FROM workout_sets
        WHERE id = ?
        """,
        (set_id,)
    )

    db.commit()
    db.close()

    return redirect(request.referrer)

@app.route("/workout/<int:workout_id>/delete", methods=["POST"])
def delete_workout(workout_id):

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    workout = db.execute(
        """
        SELECT id
        FROM workouts
        WHERE id = ? AND user_id = ?
        """,
        (workout_id, session["user_id"])
    ).fetchone()

    if workout is None:
        db.close()
        return "Workout not found", 404

    db.execute(
        """
        DELETE FROM workout_sets
        WHERE workout_id = ?
        """,
        (workout_id,)
    )

    db.execute(
        """
        DELETE FROM workouts
        WHERE id = ?
        """,
        (workout_id,)
    )

    db.commit()
    db.close()

    return redirect("/workouts")
