from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
import re
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
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # check that credentials arent already in use
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))
           
        # check that email is a valid email
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            flash("Invalid email format.", "error")
            return redirect(url_for("register"))

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="shelfspace"
        )
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM customer WHERE Email = %s", (email,))
        if cursor.fetchone():
            flash("An account with this email already exists.", "error")
            cursor.close()
            connection.close()
            return redirect(url_for("register"))

        cursor.execute("SELECT * FROM customer WHERE Username = %s", (username,))
        if cursor.fetchone():
            flash("Username is already taken.", "error")
            cursor.close()
            connection.close()
            return redirect(url_for("register"))

        # need to implement password hashing: hashed_password = generate_password_hash(password)

        insert_query = """
            INSERT INTO customer (Username, Email, Password)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (username, email, password))
        connection.commit()

        new_user_id = cursor.lastrowid

        cursor.close()
        connection.close()

        user = User(id=new_user_id, username=username, role="customer")

        login_user(user)

        flash("Account created successfully!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ----- Homepage -----
@app.route("/")
def home():
    return render_template("home.html")


# ----- Account Details ------ 
@app.route("/accountdetails", methods=["GET", "POST"])
@login_required
def accountdetails():
    if request.method == "POST":

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="shelfspace"
        )
        cursor = connection.cursor(dictionary=True)

        if "email" in request.form:
            new_email = request.form.get("email")

            # Validate email format
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", new_email):
                flash("Invalid email format.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("accountdetails"))

            # Check if email already exists
            cursor.execute("SELECT * FROM customer WHERE Email = %s AND CustomerID != %s", (new_email, current_user.id))
            if cursor.fetchone():
                flash("That email is already in use.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("accountdetails"))

            # Update email
            cursor.execute("UPDATE customer SET Email = %s WHERE CustomerID = %s", (new_email, current_user.id))
            connection.commit()

            flash("Email updated successfully!", "success")

            cursor.close()
            connection.close()
            return redirect(url_for("accountdetails"))

        if "password" in request.form:
            current_pw = request.form.get("password")
            new_pw = request.form.get("new_password")

            # Fetch current hashed password from DB
            cursor.execute("SELECT Password FROM customer WHERE CustomerID = %s", (current_user.id,))
            row = cursor.fetchone()

            if not row:
                flash("Unexpected error finding your account.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("accountdetails"))

            stored_pw = row["Password"]

            # Check if current password matches
            if (stored_pw != current_pw):
                flash("Current password is incorrect.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("accountdetails"))

            # Update password
            cursor.execute("UPDATE customer SET Password = %s WHERE CustomerID = %s", (new_pw, current_user.id))
            connection.commit()

            flash("Password updated successfully!", "success")

            cursor.close()
            connection.close()
            return redirect(url_for("accountdetails"))

        cursor.close()
        connection.close()

    return render_template("accountdetails.html")

@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor()

    # Delete from correct table based on user role
    if current_user.role == "customer":
        cursor.execute("DELETE FROM customer WHERE CustomerID = %s", (current_user.id,))
    else:  # employee
        cursor.execute("DELETE FROM employee WHERE EmployeeID = %s", (current_user.id,))

    connection.commit()
    cursor.close()
    connection.close()

    logout_user()
    flash("Your account has been deleted.", "success")
    return redirect(url_for("home"))

# ----- Display Books -----
@app.route("/books")
@login_required
def books():
    connection = mysql.connector.connect(host="localhost", user="root", password="", database="ShelfSpace")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book")
    books = cursor.fetchall()
    connection.close()
    return render_template("books.html", books=books)

# ----- Book Detail -----
@app.route("/books/<isbn>")
@login_required
def book_detail(isbn):
    connection = mysql.connector.connect(host="localhost", user="root", password="", database="ShelfSpace")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book WHERE ISBN=%s", (isbn,))
    book = cursor.fetchone()
    cursor.execute("SELECT r.text, r.rating, u.username FROM review r JOIN users u ON r.user_id=u.user_id WHERE r.ISBN=%s", (isbn,))
    reviews = cursor.fetchall()
    connection.close()
    return render_template("book_detail.html", book=book, reviews=reviews)

# ----- Employee Add Book -----
@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():
    if current_user.role != "employee":
        return "Access Denied"
    if request.method == "POST":
        # Add book to database
        pass
    return render_template("employee_add_book.html")


if __name__ == "__main__":
    app.run(debug=True)
