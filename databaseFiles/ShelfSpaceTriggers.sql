-- ShelfSpace 
-- triggers

-- reduce stock quantity when an item is added to purchase item
DELIMITER //
CREATE TRIGGER after_purchaseitem_insert
AFTER INSERT ON PurchaseItem
FOR EACH ROW
BEGIN
    UPDATE Book
    SET StockQty = StockQty - NEW.Quantity 
    WHERE ISBN = NEW.ISBN;
END;
//
DELIMITER ;


-- update the total price of a Purchase when more items are added
DELIMITER //
CREATE TRIGGER after_purchaseitem_add
AFTER INSERT ON PurchaseItem
FOR EACH ROW
BEGIN
    UPDATE Purchase P
    JOIN Book B ON B.ISBN = NEW.ISBN
    SET P.TotalPrice = P.TotalPrice + (B.Price * NEW.Quantity)
    WHERE P.PurchaseID = NEW.PurchaseID;
END;
//
DELIMITER ;


-- update stock when a purchase item is deleted
DELIMITER //
CREATE TRIGGER after_purchaseitem_delete
AFTER DELETE ON PurchaseItem
FOR EACH ROW
BEGIN
    UPDATE Book
    SET StockQty = StockQty + OLD.Quantity
    WHERE ISBN = OLD.ISBN;
END;
//
DELIMITER ;


-- do not allow a negative stock 
DELIMITER //
CREATE TRIGGER before_book_update
BEFORE UPDATE ON Book
FOR EACH ROW
BEGIN
    IF NEW.StockQty < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock cannot be negative';
    END IF;
END;
//
DELIMITER ;


-- log whena an employee moderates a review 
DELIMITER //
CREATE TRIGGER after_review_update
AFTER UPDATE ON Review
FOR EACH ROW
BEGIN
    IF OLD.Rating <> NEW.Rating OR OLD.ReviewText <> NEW.ReviewText THEN
        INSERT INTO ReviewLog (ReviewID, EmployeeID, Action, ActionDate)
        VALUES (NEW.ReviewID, NEW.ModeratedBy, 'Modified', NOW());
    END IF;
END;
//
DELIMITER ;


-- review ratings can only be numerically between 1-5 
DELIMITER //
CREATE TRIGGER before_review_insert
BEFORE INSERT ON Review
FOR EACH ROW
BEGIN
    IF NEW.Rating < 1 OR NEW.Rating > 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Rating must be between 1 and 5';
    END IF;
END;
//
DELIMITER ;


