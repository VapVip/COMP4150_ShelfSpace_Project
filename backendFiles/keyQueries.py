import mysql.connector
from mysql.connector import errorcode

# gather user inputs for mysql server, enter the username and pw created on install
username = input('Enter your MySQL Server username: ')
password = input('Enter your MySQL Server password: ')
print("")

# attempt connection
try:
    connection = mysql.connector.connect(user=username,
                                         password=password,
                                         host='localhost',
                                         database='shelfspaceDB')

# catch exceptions
except mysql.connector.Error as err:
    # bad username and pw
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Invalid credentials")

    # invalid db (run the createDB first)
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")

    # catch other errors
    else:
        print("Cannot connect:", err)

# if connection successful
else:

    # get all books below a specific stock quantity
    def get_books_below_stock(amt):
        conn = mysql.connector.connect(user=username,
                                             password=password,
                                             host='localhost',
                                             database='shelfspaceDB')
        cursor = conn.cursor(dictionary=True)
        currQuery = """
                SELECT title, quantity
                FROM book
                WHERE quantity < %s;
            """
        cursor.execute(currQuery, (amt,))
        results = cursor.fetchall()
        conn.close()
        return results

    # get all purchases made by a specific customer
    def get_purchases_by_customer(customer_id):
        conn = mysql.connector.connect(user=username,
                                             password=password,
                                             host='localhost',
                                             database='shelfspaceDB')
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT P.purchaseID, P.purchaseDate, P.purchaseTotal, B.title, PI.quantity
            FROM purchase P
            JOIN purchaseItem PI ON P.purchaseID = PI.purchaseID
            JOIN book B ON PI.ISBN = B.ISBN
            WHERE P.customerID = %s;
        """
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    # get average rating of a book
    def get_average_rating(isbn):
        conn = mysql.connector.connect(user=username,
                                       password=password,
                                       host='localhost',
                                       database='shelfspaceDB')
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT B.Title, AVG(R.Rating) AS AvgRating
            FROM Book B
            JOIN Review R ON B.ISBN = R.ISBN
            WHERE B.ISBN = %s
            GROUP BY B.Title;
        """
        cursor.execute(query, (isbn,))
        result = cursor.fetchone()
        conn.close()
        return result

    # get the top sellers list
    def get_top_selling_books(limit):
        conn = mysql.connector.connect(user=username,
                                       password=password,
                                       host='localhost',
                                       database='shelfspaceDB')
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT B.title, SUM(PI.quantity) AS totalSold
            FROM purchaseItem PI
            JOIN book B ON PI.ISBN = B.ISBN
            GROUP BY B.title
            ORDER BY totalSold DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    # get customers with most purchases
    def get_top_customers(limit):
        conn = mysql.connector.connect(user=username,
                                       password=password,
                                       host='localhost',
                                       database='shelfspaceDB')
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT C.username, COUNT(P.purchaseID) AS numPurchases
            FROM customer C
            JOIN purchase P ON C.customerID = P.customerID
            GROUP BY C.username
            ORDER BY numPurchases DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    # test cases for key queries
    # test the get_top_customers query
    print("Top 3 customers with highest number of purchases:")
    for row in get_top_customers(3):
        print(f"{row['username']}: {row['numPurchases']} purchases")
    print("")

    # test the get_top_selling_books query
    print("Top 3 best sellers:")
    for row in get_top_selling_books(3):
        print(f"{row['totalSold']} copies of {row['title']} sold")
    print("")

    # test the get_average_rating query
    print("Average book rating:")
    book = get_average_rating(9780147514011)
    if book:
        print(f"{book['Title']} has an average rating of {book['AvgRating']:.2f}")
    else:
        print("No reviews found for that ISBN")
    print("")

    # test the get_books_below_stock query
    print("Books with less than 30 in stock:")
    for row in get_books_below_stock(30):
        print(f"{row['title']} has {row['quantity']} copies left in stock")
    print("")

    # test the get_purchases_by_customer query
    print("All books purchased by customer with ID of 1234:")
    for row in get_purchases_by_customer(1234):
        print(f"Purchase #{row['purchaseID']}: {row['title']} x{row['quantity']} (${row['purchaseTotal']})")
    print("")

    # close connection
    connection.close()

