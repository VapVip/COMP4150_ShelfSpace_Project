-- ShelfSpace
-- stored procedures

-- add a new purchase
DELIMITER //
CREATE PROCEDURE AddPurchase(
    IN p_CustomerID INT,
    IN p_TotalPrice DECIMAL(10,2)
)
BEGIN
    INSERT INTO Purchase (PurchaseDate, TotalPrice, CustomerID)
    VALUES (CURDATE(), p_TotalPrice, p_CustomerID);
END;
//
DELIMITER ;


-- add a new book for employee doing stock
DELIMITER //
CREATE PROCEDURE AddBook(
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
END;
//
DELIMITER ;


-- update stock quantity when book is sold
DELIMITER //
CREATE PROCEDURE UpdateStock(
    IN p_ISBN BIGINT,
    IN p_Quantity INT
)
BEGIN
    UPDATE Book
    SET StockQty = StockQty - p_Quantity
    WHERE ISBN = p_ISBN;
END;
//
DELIMITER ;


-- list all books in desired genre
DELIMITER //
CREATE PROCEDURE GetBooksByGenre(IN p_Genre VARCHAR(50))
BEGIN
    SELECT ISBN, Title, Author, Price, StockQty
    FROM Book
    WHERE Genre = p_Genre;
END;
//
DELIMITER ;


-- add new review for book when customer submits one 
DELIMITER //
CREATE PROCEDURE AddReview(
    IN p_CustomerID INT,
    IN p_ISBN BIGINT,
    IN p_Rating INT,
    IN p_ReviewText TEXT
)
BEGIN
    INSERT INTO Review (Rating, ReviewText, Date, CustomerID, ISBN)
    VALUES (p_Rating, p_ReviewText, CURDATE(), p_CustomerID, p_ISBN);
END;
//
DELIMITER ;