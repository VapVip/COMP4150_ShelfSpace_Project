-- ShelfSpace
-- checking which books have low stock quantity 
SELECT Title, StockQty 
FROM Book
WHERE StockQty < 20;

-- show all books by a certain author / search for books by author 
SELECT ISBN, Title, Genre, Price
FROM Book
WHERE Author LIKE '%John Green%';

-- get all purchases made by a customer from CustomerID
SELECT P.PurchaseID, P.PurchaseDate, P.TotalPrice, B.Title, PI.Quantity
FROM Purchase P
JOIN PurchaseItem PI ON P.PurchaseID = PI.PurchaseID
JOIN Book B ON PI.ISBN = B.ISBN
WHERE P.CustomerID = 1234;

-- show average rating for a book 
SELECT B.Title, AVG(R.Rating) AS AvgRating
FROM Book B
JOIN Review R ON B.ISBN = R.ISBN
WHERE B.ISBN = 9780147514011
GROUP BY B.Title;

-- show reviews for a book
SELECT R.Rating, R.ReviewText, R.Date, C.Username
FROM Review R
JOIN Customer C ON R.CustomerID = C.CustomerID
WHERE R.ISBN = 9780439023528
ORDER BY R.Date DESC;

-- list the top 5 best selling books 
SELECT B.Title, SUM(PI.Quantity) AS TotalSold
FROM PurchaseItem PI
JOIN Book B ON PI.ISBN = B.ISBN
GROUP BY B.Title
ORDER BY TotalSold DESC
LIMIT 5;

-- show customers with the most purchases
SELECT C.Username, COUNT(P.PurchaseID) AS NumPurchases
FROM Customer C
JOIN Purchase P ON C.CustomerID = P.CustomerID
GROUP BY C.Username
ORDER BY NumPurchases DESC;