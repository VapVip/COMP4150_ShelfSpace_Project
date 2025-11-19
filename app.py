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


# ----- Display Books -----
@app.route("/books")
@login_required
def books():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # Get search, filter, and sort from query parameters
    search_query = request.args.get("search", "")
    genre_filter = request.args.get("genre", "all")
    sort_by = request.args.get("sort", "title")  # default sort by title

    # Base query
    query = "SELECT ISBN, Title, Author, Genre, Price FROM Book"
    params = []

    # Apply search and genre filter
    conditions = []
    if search_query:
        conditions.append("(Title LIKE %s OR Author LIKE %s)")
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term])
    if genre_filter != "all":
        conditions.append("Genre = %s")
        params.append(genre_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Apply sorting
    if sort_by == "price_asc":
        query += " ORDER BY Price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY Price DESC"
    else:
        query += " ORDER BY Title ASC"

    cursor.execute(query, params)
    books = cursor.fetchall()

    # Add average rating for each book
    for book in books:
        cursor.execute("SELECT AVG(Rating) AS avg_rating FROM Review WHERE ISBN=%s", (book['ISBN'],))
        avg = cursor.fetchone()['avg_rating']
        book['avg_rating'] = round(avg, 1) if avg else None

    # Get all unique genres for filtering dropdown
    cursor.execute("SELECT DISTINCT Genre FROM Book")
    genres = [row['Genre'] for row in cursor.fetchall() if row['Genre']]
    
    # Get all unique authors for filtering dropdown
    cursor.execute("SELECT DISTINCT Author FROM Book")
    authors = [row['Author'] for row in cursor.fetchall() if row['Author']]


    connection.close()

    return render_template(
        "books.html",
        books=books,
        genres=genres,
        authors=authors,   
        search_query=search_query,
        genre_filter=genre_filter,
        sort_by=sort_by
)



# ----- Book Detail -----
@app.route("/books/<isbn>")
@login_required
def book_detail(isbn):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # Get book details
    cursor.execute("SELECT * FROM Book WHERE ISBN = %s", (isbn,))
    book = cursor.fetchone()

    # Get reviews + customer usernames
    cursor.execute("""
        SELECT 
            r.ReviewText,
            r.Rating,
            c.Username,
            r.Date
        FROM Review r
        JOIN Customer c ON r.CustomerID = c.CustomerID
        WHERE r.ISBN = %s
        ORDER BY r.Date DESC
    """, (isbn,))
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
    

# ----- Employee Edit Book -----
@app.route("/books/edit/<isbn>", methods=["GET", "POST"])
@login_required
def edit_book(isbn):
    if current_user.role not in ["Manager", "Staff", "Admin"]:
        return "Access Denied"


    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # Get the book info
    cursor.execute("SELECT * FROM Book WHERE ISBN=%s", (isbn,))
    book = cursor.fetchone()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        price = request.form.get("price")

        cursor.execute(
            "UPDATE Book SET Title=%s, Author=%s, Genre=%s, Price=%s WHERE ISBN=%s",
            (title, author, genre, price, isbn)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("books"))

    cursor.close()
    connection.close()
    return render_template("employee_edit_book.html", book=book)


# ----- Employee Delete Book -----
@app.route("/books/delete/<isbn>", methods=["POST"])
@login_required
def delete_book(isbn):
    if current_user.role not in ["Manager", "Admin"]:
        return "Access Denied"


    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Book WHERE ISBN=%s", (isbn,))
    connection.commit()

    cursor.close()
    connection.close()

    flash("Book deleted successfully!", "success")
    return redirect(url_for("books"))


# ----- Customer Add to Cart -----
@app.route("/cart/add/<isbn>", methods=["POST"])
@login_required
def add_to_cart(isbn):
    if current_user.role != "customer":
        return "Access Denied"

    # Insert into Cart table
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Cart (CustomerID, ISBN, Quantity) VALUES (%s, %s, 1) "
                   "ON DUPLICATE KEY UPDATE Quantity = Quantity + 1",
                   (current_user.id, isbn))
    connection.commit()
    cursor.close()
    connection.close()
    flash("Book added to cart!", "success")
    return redirect(url_for("books"))


# ----- Customer Add to Wishlist -----
@app.route("/wishlist/add/<isbn>", methods=["POST"])
@login_required
def add_to_wishlist(isbn):
    if current_user.role != "customer":
        return "Access Denied"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Wishlist (CustomerID, ISBN) VALUES (%s, %s) "
                   "ON DUPLICATE KEY UPDATE DateAdded=NOW()",
                   (current_user.id, isbn))
    connection.commit()
    cursor.close()
    connection.close()
    flash("Book added to wishlist!", "success")
    return redirect(url_for("books"))


# ----- Customer View Wishlist -----
@app.route("/wishlist")
@login_required
def view_wishlist():
    if current_user.role != "customer":
        return "Access Denied"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.ISBN, b.Title, b.Author, b.Price
        FROM Wishlist w
        JOIN Book b ON w.ISBN = b.ISBN
        WHERE w.CustomerID = %s
        ORDER BY w.DateAdded DESC
    """, (current_user.id,))

    wishlist_books = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("wishlist.html", books=wishlist_books)


# ----- View Customer Cart -----
@app.route("/cart")
@login_required
def view_cart():
    if current_user.role != "customer":
        return "Access Denied"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # Get cart items for this customer
    cursor.execute("""
        SELECT c.ISBN, b.Title, b.Author, b.Price, c.Quantity
        FROM Cart c
        JOIN Book b ON c.ISBN = b.ISBN
        WHERE c.CustomerID = %s
    """, (current_user.id,))
    cart_items = cursor.fetchall()

    connection.close()

    return render_template("cart.html", cart_items=cart_items)




if __name__ == "__main__":
    app.run(debug=True)
