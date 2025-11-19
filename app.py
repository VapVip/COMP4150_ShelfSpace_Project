from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "secret_key_here"

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

# ---------------------- USER MODEL ----------------------
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# This function tells Flask-Login how to get a User object from a user_id
@login_manager.user_loader
def load_user(user_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor(dictionary=True)
    query = """
            (
                SELECT CustomerID AS id, Username AS username, 'customer' AS role
                FROM customer
                WHERE CustomerID = %s
            )
            UNION ALL
            (
                SELECT EmployeeID AS id, Name AS username, Role AS role
                FROM employee
                WHERE EmployeeID = %s
            )
            LIMIT 1;
            """
    cursor.execute(query, (user_id, user_id))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row:
        return User(row["id"], row["username"], row["role"])
    return None

# ----- User Login, Register, Logout -----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            print("ATTEMPTING SQL CONNECTION:")
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="shelfspace"
            )
            cursor = connection.cursor(dictionary=True)
        except BaseException as e:
            print("UNCAUGHT DATABASE ERROR:", e)

        print("DATABASE CONNECTION SUCCESSFUL!")

        print("BEGINNING SEARCH BY EMAIL")
        # Look for user by email
        query = """
                (
                    SELECT CustomerID AS id, Username AS username, Email AS email, Password AS password, 'customer' AS role
                    FROM customer
                    WHERE Email = %s
                )
                UNION ALL
                (
                    SELECT EmployeeID AS id, Name AS username, Email AS email, Password AS password, Role AS role
                    FROM employee
                    WHERE Email = %s
                )
                LIMIT 1;
                """
        cursor.execute(query, (email, email))
        user_row = cursor.fetchone()

        print("EMAIL QUERY COMPLETE")

        cursor.close()
        connection.close()

        if user_row is None:
            flash("No account found with that email.", "error")
            return redirect(url_for("login"))

        # Check password
        if user_row["password"] != password:
            flash("Incorrect password.", "error")
            return redirect(url_for("login"))

        # Create a User object for Flask-Login
        user = User(
            id=user_row["id"],
            username=user_row["username"],
            role=user_row["role"]
        )

        # Log the user in
        login_user(user)

        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))

    # GET request → show the login page
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Add registration logic here
    pass

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ----- Homepage -----
@app.route("/")
def home():
    return render_template("home.html")

# ----- Display Books -----
@app.route("/books")
@login_required
def books():
    connection = mysql.connector.connect(host="localhost", user="root", password="", database="shelfspace")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book")
    books = cursor.fetchall()
    connection.close()
    return render_template("books.html", books=books)


if __name__ == "__main__":
    app.run(debug=True)
