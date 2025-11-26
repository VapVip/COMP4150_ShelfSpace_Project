import mysql.connector
from mysql.connector import errorcode

# gather user inputs for mysql server, enter the username and pw created on install
username = input('Enter your MySQL Server username: ')
password = input('Enter your MySQL Server password: ')
print()

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
    # create cursor
    cursor = connection.cursor()

    # select db
    cursor.execute("USE shelfspaceDB")

    try:
        # populate customer table with sample data
        currQuery = "INSERT INTO customer (customerID, username, email, password) VALUES (%s, %s, %s, %s)"
        currValues = [(1234, 'PageTurner42', 'pageTurner42@gmail.com', 'PgTr!9842'),
                      (5678, 'NovelNook23', 'novelnook23@outlook.com', 'NvlNk#2323'),
                      (9101, 'ReadRite09', 'readrite09@gmail.com', 'RdRt@0909'),
                      (1213, 'BookishSoul', 'bookishsoul@outlook.ca', 'BkSh!Soul24')]
        cursor.executemany(currQuery, currValues)

        # populate employee table with sample data
        currQuery = "INSERT INTO employee (employeeID, name, email, password, role) VALUES (%s, %s, %s, %s, %s)"
        currValues = [(2001, 'Larisa Renaud', 'lrenaud@shelfspsace.com', 'BookL0ver94', 'Manager'),
                      (2002, 'Liam Thompson', 'lthompson@shelfspace.com', 'LTh#7890', 'Staff'),
                      (2003, 'Sophia Nguyen', 'snguyen@shelfspace.com', 'SoNg!453', 'Admin'),
                      (2004, 'Daniel Brooks', 'dbrooks@shelfspace.com', 'DbRk$1122', 'Staff')]
        cursor.executemany(currQuery, currValues)

        # populate book table with sample data
        currQuery = "INSERT INTO book (ISBN, title, author, genre, description, price, quantity) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        currValues = [(9780439023528, 'The Hunger Games', 'Suzanne Collins', 'Dystopian', 'A thrilling novel set in a dystopian future where teens fight for survival in a televised competition.', 19.99, 40),
                      (9780147514011, 'Little Women', 'Louisa May Alcott', 'Classic', 'A timeless story of four sisters growing up and finding their paths during the Civil War era.', 24.50, 18),
                      (9781408855652, 'Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 'Fantasy', 'The first installment in the Harry Potter series, where a young boy discovers he is a wizard.', 15.00, 30),
                      (9781594138577, 'Paper Towns', 'John Green', 'Young Adult', 'A coming-of-age story that explores friendship, love, and the search for identity.', 16.95, 20),
                      (9781338878936, 'Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 'The second book in the Harry Potter series, full of magic, mystery, and adventure.', 16.95, 45),
                      (9780735211292, 'Atomic Habits', 'James Clear', 'Self-Help', 'A practical guide on how to build good habits, break bad ones, and master the tiny behaviors that lead to remarkable results.', 36.00, 12),
                      (9780545227247, 'Catching Fire', 'Suzanne Collins', 'Dystopian', 'The second installment in The Hunger Games series, where the stakes are higher and the action even more intense.', 15.99, 35)]
        cursor.executemany(currQuery, currValues)

        # populate review table with sample data
        currQuery = "INSERT INTO review (reviewID, rating, reviewText, reviewDate, customerID, ISBN) VALUES (%s, %s, %s, %s, %s, %s)"
        currValues = [(301, 5, 'Absolutely gripping from start to finish! The world-building and characters are incredible.', '2025-10-15', 1234, 9781408855652),
                      (302, 4, 'A heartwarming and beautifully written classic. The sisters feel so real and relatable.', '2025-10-20', 5678, 9780147514011),
                      (303, 5, 'A masterpiece that stays with you long after reading. A must-read for everyone.', '2025-10-25', 9101, 9780439023528),
                      (304, 3, 'Interesting mystery but a bit slow in the middle. Still worth reading for the ending.', '2025-11-02', 1213, 9781594138577),
                      (305, 4, 'Great sequel with even more action and tension. Can’t wait for the next one!', '2025-11-05', 1234, 9780545227247),
                      (306, 5, 'Absolutely loved the magical world and character development. Rowling never disappoints!', '2025-11-06', 5678, 9781338878936)]
        cursor.executemany(currQuery, currValues)

        # populate purchase table with sample data
        currQuery = "INSERT INTO purchase (purchaseID, purchaseDate, purchaseTotal, customerID) VALUES (%s, %s, %s, %s)"
        currValues = [(4001, '2025-10-12', 19.99, 1234),
                      (4002, '2025-10-18', 49.00, 5678),
                      (4003, '2025-10-25', 15.00, 9101),
                      (4004, '2025-11-01', 16.95, 1213),
                      (4005, '2025-11-07', 32.94, 1234),
                      (4006, '2025-11-08', 108.00, 5678),
                      (4007, '2025-11-09', 15.00, 9101)]
        cursor.executemany(currQuery, currValues)

        # populate purchaseItem table with sample data
        currQuery = "INSERT INTO purchaseItem (purchaseID, ISBN, quantity) VALUES (%s, %s, %s)"
        currValues = [(4001, 9780439023528, 1),
                      (4002, 9780147514011, 2),
                      (4003, 9781408855652, 1),
                      (4004, 9781594138577, 1),
                      (4005, 9780545227247, 1),
                      (4005, 9781594138577, 1),
                      (4006, 9781338878936, 2),
                      (4007, 9780735211292, 3),
                      (4007, 9781408855652, 1)]
        cursor.executemany(currQuery, currValues)


        # drop stored procedures
        cursor.execute("DROP PROCEDURE IF EXISTS AddPurchase")
        cursor.execute("DROP PROCEDURE IF EXISTS AddBook")
        cursor.execute("DROP PROCEDURE IF EXISTS UpdateStock")
        cursor.execute("DROP PROCEDURE IF EXISTS GetBooksByGenre")
        cursor.execute("DROP PROCEDURE IF EXISTS AddReview")

        # implement stored procedures
        cursor.execute("""CREATE PROCEDURE AddPurchase(
                              IN p_CustomerID INT,
                              IN p_TotalPrice DECIMAL(10,2)
                          )
                          BEGIN
                              INSERT INTO Purchase (PurchaseDate, TotalPrice, CustomerID)
                              VALUES (CURDATE(), p_TotalPrice, p_CustomerID);
                          END;""")

        cursor.execute("""CREATE PROCEDURE AddBook(
                              IN p_ISBN BIGINT,
                              IN p_Title VARCHAR(255),
                              IN p_Author VARCHAR(255),
                              IN p_Genre VARCHAR(50),
                              IN p_Description TEXT,
                              IN p_Price DECIMAL(10,2),
                              IN p_StockQty INT
                          )
                          BEGIN
                              INSERT INTO Book (ISBN, Title, Author, Genre, Description, Price, StockQty)
                              VALUES (p_ISBN, p_Title, p_Author, p_Genre, p_Description, p_Price, p_StockQty);
                          END;""")

        cursor.execute("""CREATE PROCEDURE GetBooksByGenre(IN p_Genre VARCHAR(50))
                          BEGIN
                              SELECT ISBN, Title, Author, Price, StockQty
                              FROM Book
                              WHERE Genre = p_Genre;
                          END;""")

        cursor.execute("""CREATE PROCEDURE UpdateStock(
                            IN p_ISBN BIGINT,
                            IN p_Quantity INT
                          )
                          BEGIN
                            UPDATE Book
                            SET StockQty = StockQty - p_Quantity
                            WHERE ISBN = p_ISBN;
                          END;""")

        cursor.execute("""CREATE PROCEDURE AddReview(
                              IN p_CustomerID INT,
                              IN p_ISBN BIGINT,
                              IN p_Rating INT,
                              IN p_ReviewText TEXT
                          )
                          BEGIN
                              INSERT INTO Review (Rating, ReviewText, Date, CustomerID, ISBN)
                              VALUES (p_Rating, p_ReviewText, CURDATE(), p_CustomerID, p_ISBN);
                          END;""")

        # commit changes
        connection.commit()

    # duplicate entry (running this script more than once)
    except mysql.connector.IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print("Data not added to database, duplicate entries")
        else:
            print("Integrity Error:", err)

    # display all data from database
    cursor.execute("SHOW TABLES;")
    print("Tables:")
    for (table,) in cursor.fetchall():
        print("-", table)

    print("\nCustomer Contents:")
    cursor.execute("SELECT * FROM customer;")
    for row in cursor.fetchall():
        print(row)

    print("\nEmployee Contents:")
    cursor.execute("SELECT * FROM employee;")
    for row in cursor.fetchall():
        print(row)

    print("\nBook Contents:")
    cursor.execute("SELECT * FROM book;")
    for row in cursor.fetchall():
        print(row)

    print("\nReview Contents:")
    cursor.execute("SELECT * FROM review;")
    for row in cursor.fetchall():
        print(row)

    print("\nPurchase Contents:")
    cursor.execute("SELECT * FROM purchase;")
    for row in cursor.fetchall():
        print(row)

    print("\nPurchaseItem Contents:")
    cursor.execute("SELECT * FROM purchaseItem;")
    for row in cursor.fetchall():
        print(row)

    print("\nProcedures:")
    cursor.execute("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
    for row in cursor.fetchall():
        print(row)

    # close connection
    connection.close()

