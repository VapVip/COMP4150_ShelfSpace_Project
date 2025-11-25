import mysql.connector
from mysql.connector import errorcode

# gather user inputs for mysql server, enter the username and pw created on install
username = input('Enter your MySQL Server username: ')
password = input('Enter your MySQL Server password: ')

# attempt connection
try:
    connection = mysql.connector.connect(user=username,
                                         password=password,
                                         host='localhost')

# catch exceptions
except mysql.connector.Error as err:
    # bad username and pw
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Invalid credentials")
    # catch other errors
    else:
        print("Cannot connect:", err)

# if connection successful
else:
    # success message
    print("Successfully connected to MySQL Server")

    # define cursor
    cursor = connection.cursor()

    # drop old database, clears the contents of database if re-running this script
    cursor.execute(f"DROP DATABASE IF EXISTS shelfspaceDB")
    print(f"Dropped old database if it existed")

    # create the shelfspace database
    cursor.execute("CREATE DATABASE IF NOT EXISTS shelfspaceDB")

    # select database
    cursor.execute("USE shelfspaceDB")

    # create customer table
    cursor.execute("""CREATE TABLE IF NOT EXISTS customer (
                            customerID INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(25) NOT NULL UNIQUE,
                            email VARCHAR(25) NOT NULL UNIQUE,
                            password VARCHAR(25) NOT NULL UNIQUE
                        )""")

    # create employee table
    cursor.execute("""CREATE TABLE IF NOT EXISTS employee (
                            employeeID INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(25) NOT NULL UNIQUE,
                            email VARCHAR(25) NOT NULL UNIQUE,
                            password VARCHAR(25) NOT NULL UNIQUE,
                            role VARCHAR(25) NOT NULL
                        )""")

    # create book table
    cursor.execute("""CREATE TABLE IF NOT EXISTS book (
                            ISBN BIGINT PRIMARY KEY,
                            title VARCHAR(100) NOT NULL,
                            author VARCHAR(35) NOT NULL,
                            genre VARCHAR(35),
                            description TEXT,
                            price DECIMAL(10,2) NOT NULL,
                            quantity INT DEFAULT 0,
                            employeeID INT,
                            FOREIGN KEY (employeeID)
                            REFERENCES employee(employeeID)
                            ON DELETE SET NULL
                            ON UPDATE CASCADE
                        )""")

    # create review table
    cursor.execute("""CREATE TABLE IF NOT EXISTS review (
                            reviewID INT AUTO_INCREMENT PRIMARY KEY,
                            rating INT NOT NULL,
                            reviewText TEXT,
                            reviewDate DATE NOT NULL,
                            customerID INT,
                            ISBN BIGINT,
                            FOREIGN KEY (ISBN)
                            REFERENCES book(ISBN)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE,
                            FOREIGN KEY (customerID)
                            REFERENCES customer(customerID)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                        )""")

    # create purchase table
    cursor.execute("""CREATE TABLE IF NOT EXISTS purchase (
                            purchaseID INT AUTO_INCREMENT PRIMARY KEY,
                            purchaseDate DATETIME NOT NULL,
                            purchaseTotal DECIMAL(10,2) NOT NULL,
                            customerID INT NOT NULL,
                            FOREIGN KEY (customerID)
                            REFERENCES customer(customerID)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                        )""")

    # create purchaseItem table
    cursor.execute("""CREATE TABLE IF NOT EXISTS purchaseItem (
                            purchaseID INT NOT NULL,
                            ISBN BIGINT NOT NULL,
                            quantity INT NOT NULL,
                            FOREIGN KEY (ISBN)
                            REFERENCES book(ISBN)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE,
                            FOREIGN KEY (purchaseID)
                            REFERENCES purchase(purchaseID)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
                        )""")

    # commit to database
    connection.commit()

    # success message
    print("Successfully created the shelfspaceDB database")

    # close connection
    connection.close()
