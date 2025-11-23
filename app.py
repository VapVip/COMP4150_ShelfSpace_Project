from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
import re
from werkzeug.security import generate_password_hash, check_password_hash

# flask setup
app = Flask(__name__)
app.secret_key = "secret_key_here"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# flask user login
from flask_login import UserMixin

# flask user class definition
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# flask login user object from user id
@login_manager.user_loader
def load_user(user_id):
    # connect to db
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace",
        autocommit=True  
    )
    cursor = connection.cursor(dictionary=True)

    # run query to get user info
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

# user login def
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # connect to db
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

        # search for user email
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
        cursor.close()
        connection.close()

        if user_row is None:
            flash("No account found with that email.", "error")
            return redirect(url_for("login"))

        # check if password correct
        if user_row["password"] != password:
            flash("Incorrect password.", "error")
            return redirect(url_for("login"))

        # create user profile
        user = User(
            id=user_row["id"],
            username=user_row["username"],
            role=user_row["role"]
        )

        # log in the user
        login_user(user)

        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))

    # show login page
    return render_template("login.html")

# user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # check that all fields filled
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))
           
        # check that email is a valid email format
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            flash("Invalid email format.", "error")
            return redirect(url_for("register"))

        # connect to db
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="shelfspace"
        )
        cursor = connection.cursor(dictionary=True)

        # check for email in use
        cursor.execute("SELECT * FROM customer WHERE Email = %s", (email,))
        if cursor.fetchone():
            flash("An account with this email already exists.", "error")
            cursor.close()
            connection.close()
            return redirect(url_for("register"))

        # check for username in use
        cursor.execute("SELECT * FROM customer WHERE Username = %s", (username,))
        if cursor.fetchone():
            flash("Username is already taken.", "error")
            cursor.close()
            connection.close()
            return redirect(url_for("register"))

        # insert info into db
        insert_query = """
            INSERT INTO customer (Username, Email, Password)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (username, email, password))
        connection.commit()
        new_user_id = cursor.lastrowid
        cursor.close()
        connection.close()

        # create user profile
        user = User(id=new_user_id, username=username, role="customer")

        # log user in
        login_user(user)

        # flash message
        flash("Account created successfully!", "success")
        
        # return to home page
        return redirect(url_for("home"))
    
    # show register page
    return render_template("register.html")

# user log out
@app.route("/logout")
@login_required
def logout():
    # log out user
    logout_user()

    # return to home page
    return redirect(url_for('home'))

# homepage
@app.route("/")
def home():
    # connect to db
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)
    genre_filter = request.args.get("genre", "all")

    # base query
    query = "SELECT ISBN, Title, Author, Genre, Price FROM Book"
    params = []

    # apply search and filters
    conditions = []
    if genre_filter != "all":
        conditions.append("Genre = %s")
        params.append(genre_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY Title ASC"

    cursor.execute(query, params)
    books = cursor.fetchall()

    # calculate average book rating
    for book in books:
        cursor.execute("SELECT AVG(Rating) AS avg_rating FROM Review WHERE ISBN=%s", (book['ISBN'],))
        avg = cursor.fetchone()['avg_rating']
        book['avg_rating'] = round(avg, 1) if avg else None

    # get genres fro dropdown
    cursor.execute("SELECT DISTINCT Genre FROM Book")
    genres = [row['Genre'] for row in cursor.fetchall() if row['Genre']]
    
    # get authors for dropdown
    cursor.execute("SELECT DISTINCT Author FROM Book")
    authors = [row['Author'] for row in cursor.fetchall() if row['Author']]

    connection.close()

    # show home page
    return render_template(
        "home.html",
        books=books,
        genres=genres,
        authors=authors,   
        genre_filter=genre_filter,
)

# account details page
@app.route("/account_details", methods=["GET", "POST"])
@login_required
def account_details():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        if "email" in request.form:
            new_email = request.form.get("email")

            # validate email format
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", new_email):
                flash("Invalid email format.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("account_details"))

            # check if email already exists
            cursor.execute("SELECT * FROM Customer WHERE Email = %s AND CustomerID != %s", (new_email, current_user.id))
            if cursor.fetchone():
                flash("That email is already in use.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("account_details"))

            # update email
            cursor.execute("UPDATE Customer SET Email = %s WHERE CustomerID = %s", (new_email, current_user.id))
            connection.commit()

            flash("Email updated successfully!", "success")
            cursor.close()
            connection.close()
            return redirect(url_for("account_details"))

        if "password" in request.form:
            current_pw = request.form.get("password")
            new_pw = request.form.get("new_password")

            # fetch current hashed password from DB
            cursor.execute("SELECT Password FROM Customer WHERE CustomerID = %s", (current_user.id,))
            row = cursor.fetchone()

            if not row:
                flash("Unexpected error finding your account.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("account_details"))

            stored_pw = row["Password"]

            # check if current password matches
            if stored_pw != current_pw:
                flash("Current password is incorrect.", "error")
                cursor.close()
                connection.close()
                return redirect(url_for("account_details"))

            # update password
            cursor.execute("UPDATE Customer SET Password = %s WHERE CustomerID = %s", (new_pw, current_user.id))
            connection.commit()

            flash("Password updated successfully!", "success")
            cursor.close()
            connection.close()
            return redirect(url_for("account_details"))

    # fetch all reviews by this user with book info
    cursor.execute("""
        SELECT r.ReviewID, r.Rating, r.ReviewText, r.Date, r.ISBN, b.Title AS book_title, b.Author AS book_author
        FROM Review r
        JOIN Book b ON r.ISBN = b.ISBN
        WHERE r.CustomerID = %s
    """, (current_user.id,))
    reviews = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("account_details.html", reviews=reviews)

# edit review page
@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor(dictionary=True)

    # fetch review
    cursor.execute("SELECT * FROM Review WHERE ReviewID = %s AND CustomerID = %s", (review_id, current_user.id))
    review = cursor.fetchone()
    if not review:
        flash("Review not found.", "error")
        cursor.close()
        connection.close()
        return redirect(url_for("account_details"))

    if request.method == "POST":
        new_rating = request.form.get("rating")
        new_text = request.form.get("review_text")
        cursor.execute(
            "UPDATE Review SET Rating = %s, ReviewText = %s WHERE ReviewID = %s",
            (new_rating, new_text, review_id)
        )
        connection.commit()
        flash("Review updated successfully!", "success")
        cursor.close()
        connection.close()
        return redirect(url_for("account_details"))

    cursor.close()
    connection.close()
    return render_template("edit_review.html", review=review)

# delete review
@app.route("/delete_review/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Review WHERE ReviewID = %s AND CustomerID = %s", (review_id, current_user.id))
    connection.commit()
    cursor.close()
    connection.close()
    flash("Review deleted successfully!", "success")
    return redirect(url_for("account_details"))

# employee delete review
@app.route("/delete_review_employee/<int:review_id>/<isbn>", methods=["POST"])
@login_required
def delete_review_employee(review_id, isbn):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shelfspace"
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Review WHERE ReviewID = %s", (review_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash("Review deleted successfully!", "success")
    return redirect(url_for('book_detail', isbn=isbn))

@app.route("/about")
@login_required
def about():
    return render_template(
        "about.html",
)

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
            flash("Feedback sent!", "success")
    return render_template(
        "contact.html",
)

# display books
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

    # get search, filter, and sort from query parameters
    search_query = request.args.get("search", "")
    genre_filter = request.args.get("genre", "all")
    sort_by = request.args.get("sort", "title")

    # base query
    query = "SELECT ISBN, Title, Author, Genre, Price FROM Book"
    params = []

    # apply search and genre filter
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

    # apply sorting
    if sort_by == "price_asc":
        query += " ORDER BY Price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY Price DESC"
    else:
        query += " ORDER BY Title ASC"

    cursor.execute(query, params)
    books = cursor.fetchall()

    # add average rating for each book
    for book in books:
        cursor.execute("SELECT AVG(Rating) AS avg_rating FROM Review WHERE ISBN=%s", (book['ISBN'],))
        avg = cursor.fetchone()['avg_rating']
        book['avg_rating'] = round(avg, 1) if avg else None

    # get all unique genres for filtering dropdown
    cursor.execute("SELECT DISTINCT Genre FROM Book")
    genres = [row['Genre'] for row in cursor.fetchall() if row['Genre']]
    
    # get all unique authors for filtering dropdown
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

# book detail
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

    # get book details
    cursor.execute("SELECT * FROM Book WHERE ISBN = %s", (isbn,))
    book = cursor.fetchone()

    # get reviews and customer usernames
    cursor.execute("""
        SELECT 
            r.ReviewID,
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

    # sort and filter
    sort = request.args.get("sort")  
    stars = request.args.get("stars") 

    filtered_reviews = reviews.copy()

    # filter by star rating
    if stars and stars.isdigit():
        filtered_reviews = [r for r in filtered_reviews if r["Rating"] == int(stars)]

    # sort
    if sort == "low":
        filtered_reviews = sorted(filtered_reviews, key=lambda r: r["Rating"])
    elif sort == "high":
        filtered_reviews = sorted(filtered_reviews, key=lambda r: r["Rating"], reverse=True)

    # compute average rating (use all reviews, not filtered ones)
    if reviews:
        avg_rating = sum(r["Rating"] for r in reviews) / len(reviews)
        book["avg_rating"] = round(avg_rating, 1)
    else:
        book["avg_rating"] = None

    connection.close()

    return render_template(
        "book_detail.html",
        book=book,
        reviews=reviews,                 
        filtered_reviews=filtered_reviews 
    )

# add review
@app.route('/books/<isbn>/add_review', methods=['GET', 'POST'])
@login_required
def add_review(isbn):
    if current_user.role != "customer":
        return "Access Denied"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # get the book details
    cursor.execute("SELECT * FROM Book WHERE ISBN = %s", (isbn,))
    book = cursor.fetchone()

    if request.method == 'POST':
        review_text = request.form.get('review_text')
        rating = int(request.form.get('rating', 0))

        cursor.execute("""
            INSERT INTO Review (CustomerID, ISBN, ReviewText, Rating, Date)
            VALUES (%s, %s, %s, %s, NOW())
        """, (current_user.id, isbn, review_text, rating))
        connection.commit()

        cursor.close()
        connection.close()

        flash("Review added successfully!", "success")
        return redirect(url_for('book_detail', isbn=isbn))

    cursor.close()
    connection.close()
    return render_template('add_review.html', book=book)

# employee add book
@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():
    # only employees can add books
    if current_user.role == "Customer":
        return "Access Denied", 403

    # load genres
    if request.method == "GET":
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ShelfSpace"
        )
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT DISTINCT Genre FROM Book ORDER BY Genre")
        genres = [row["Genre"] for row in cursor.fetchall() if row["Genre"]]

        cursor.close()
        connection.close()

        return render_template("add_book.html", genres=genres)

    # add book
    if request.method == "POST":
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        description = request.form['description']
        price = request.form['price']
        stock_qty = request.form['stock']

        # image uploading
        cover = request.files.get('cover')
        filename = None
        
        if cover:
            ext = os.path.splitext(cover.filename)[1]  
            filename = secure_filename(f"{isbn}{ext}")
            cover.save(os.path.join(save_path, filename))


        # insert new book into db
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ShelfSpace"
        )
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO Book (ISBN, Title, Author, Genre, Description, Price, StockQty, AddedBy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            isbn, title, author, genre,
            description, price, stock_qty,
            current_user.id
        ))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Book added successfully!", "success")
        return redirect(url_for("books"))

# edit book
@app.route("/books/edit/<isbn>", methods=["GET", "POST"])
@login_required
def edit_book(isbn):
    if current_user.role not in ["Manager", "Staff", "Admin"]:
        return "Access Denied"

    # connect to db
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)

    # fetch existing book data
    cursor.execute("SELECT * FROM Book WHERE ISBN=%s", (isbn,))
    book = cursor.fetchone()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        price = request.form.get("price")
        stockqty = request.form.get("stockqty")

        cursor.execute(
            """
            UPDATE Book
            SET Title=%s,
                Author=%s,
                Genre=%s,
                Price=%s,
                StockQty=%s
            WHERE ISBN=%s
            """,
            (title, author, genre, price, stockqty, isbn)
        )

        connection.commit()
        cursor.close()
        connection.close()

        flash("Book updated successfully!", "success")
        return redirect(url_for("books"))

    cursor.close()
    connection.close()

    return render_template("edit_book.html", book=book)

# delete book
@app.route("/books/delete/<isbn>", methods=["POST"])
@login_required
def delete_book(isbn):
    if current_user.role not in ["Manager", "Admin"]:
        return "Access Denied"
    
    # connect to db
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

# update book info
@app.route("/books/manage")
@login_required
def employee_books():
    # only employee can edit books
    if current_user.role not in ["Manager", "Staff", "Admin"]:
        return "Access Denied"
    # connect to db
    connection = mysql.connector.connect(
        host="localhost", user="root", password="", database="ShelfSpace"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Book")
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("employee_books.html", books=books)

# add to cart
@app.route("/cart/add/<isbn>", methods=["POST"])
@login_required
def add_to_cart(isbn):
    if current_user.role != "customer":
        return "Access Denied"

    # insert into cart table
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

# add to wishlist
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


# view wishlist
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

    # fetch wishlist books
    cursor.execute("""
        SELECT b.ISBN, b.Title, b.Author, b.Price
        FROM Wishlist w
        JOIN Book b ON w.ISBN = b.ISBN
        WHERE w.CustomerID = %s
        ORDER BY w.DateAdded DESC
    """, (current_user.id,))
    wishlist_books = cursor.fetchall()

    # compute average rating for each book
    for book in wishlist_books:
        cursor.execute("SELECT Rating FROM Review WHERE ISBN = %s", (book['ISBN'],))
        ratings = [r['Rating'] for r in cursor.fetchall()]
        if ratings:
            book['avg_rating'] = round(sum(ratings) / len(ratings), 1)
        else:
            book['avg_rating'] = 0.0

    cursor.close()
    connection.close()

    return render_template("wishlist.html", books=wishlist_books)

# remove from wishlist
@app.route("/wishlist/remove/<isbn>", methods=["POST"])
@login_required
def remove_from_wishlist(isbn):
    if current_user.role != "customer":
        return "Access Denied"

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Wishlist WHERE CustomerID = %s AND ISBN = %s",
                   (current_user.id, isbn))
    connection.commit()
    cursor.close()
    connection.close()

    flash("Book removed from wishlist.", "success")
    return redirect(url_for("view_wishlist"))

# view cart
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

    # fetch cart items for this customer
    cursor.execute("""
        SELECT c.ISBN, b.Title, b.Author, b.Price, c.Quantity
        FROM Cart c
        JOIN Book b ON c.ISBN = b.ISBN
        WHERE c.CustomerID = %s
    """, (current_user.id,))
    cart_items = cursor.fetchall()

    # calculate cart count
    cart_count = sum(item['Quantity'] for item in cart_items)
    connection.close()

    return render_template("cart.html", cart_items=cart_items, cart_count=cart_count)

# update cart
@app.route("/cart/update/<isbn>", methods=["POST"])
@login_required
def update_cart(isbn):
    # only customer has cart
    if current_user.role != "customer":
        return "Access Denied"

    quantity = int(request.form.get("quantity", 1))
    action = request.form.get("action")

    # check decrease or increase qty
    if action == "increase":
        quantity += 1
    elif action == "decrease":
        quantity -= 1

    quantity = max(quantity, 0)

    # connect to db
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()

    if quantity == 0:
        cursor.execute("DELETE FROM Cart WHERE CustomerID=%s AND ISBN=%s", (current_user.id, isbn))
    else:
        cursor.execute("UPDATE Cart SET Quantity=%s WHERE CustomerID=%s AND ISBN=%s", (quantity, current_user.id, isbn))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("view_cart"))

# remove from cart
@app.route("/cart/remove/<isbn>", methods=["POST"])
@login_required
def remove_from_cart(isbn):
    # only customer has cart
    if current_user.role != "customer":
        return "Access Denied"

    # connect to db
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ShelfSpace"
    )
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM Cart WHERE CustomerID=%s AND ISBN=%s",
        (current_user.id, isbn)
    )

    connection.commit()
    cursor.close()
    connection.close()

    flash("Book removed from cart.", "success")
    return redirect(url_for("view_cart"))


# cart count context processor
@app.context_processor
def inject_cart_count():
    cart_count = 0
    # only customer has cart
    if current_user.is_authenticated and current_user.role == "customer":
        # connect to db
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ShelfSpace"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT SUM(Quantity) AS total_items
            FROM Cart
            WHERE CustomerID = %s
        """, (current_user.id,))
        result = cursor.fetchone()
        if result and result["total_items"]:
            cart_count = result["total_items"]
        connection.close()
    return dict(cart_count=cart_count)

if __name__ == "__main__":
    app.run(debug=True)