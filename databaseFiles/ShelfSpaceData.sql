-- ShelfSpace
USE ShelfSpace; 

-- Sample Data for Customer 
INSERT INTO Customer (CustomerID, Username, Email, Password) VALUES 
	(1234, 'PageTurner42', 'pageTurner42@gmail.com', 'PgTr!9842'),
	(5678, 'NovelNook23', 'novelnook23@outlook.com', 'NvlNk#2323'),
	(9101, 'ReadRite09', 'readrite09@gmail.com', 'RdRt@0909'),
	(1213, 'BookishSoul', 'bookishsoul@outlook.ca', 'BkSh!Soul24');

-- Sample Data for Employee
INSERT INTO Employee (EmployeeID, Name, Email, Password, Role) VALUES
	(2001, 'Emily Carter', 'ecarter@shelfspsace.com', 'Em!lyC@2024', 'Manager'),
	(2002, 'Liam Thompson', 'lthompson@shelfspace.com', 'LTh#7890', 'Staff'),
	(2003, 'Sophia Nguyen', 'snguyen@shelfspace.com', 'SoNg!453', 'Admin'),
	(2004, 'Daniel Brooks', 'dbrooks@shelfspace.com', 'DbRk$1122', 'Staff');
   
-- Sample Data for Book
INSERT INTO Book (ISBN, Title, Author, Genre, Description, Price, StockQty) VALUES
	(9780439023528, 'The Hunger Games', 'Suzanne Collins', 'Dystopian', 'A thrilling novel set in a dystopian future where teens fight for survival in a televised competition.', 19.99, 40),
	(9780147514011, 'Little Women', 'Louisa May Alcott', 'Classic', 'A timeless story of four sisters growing up and finding their paths during the Civil War era.', 24.50, 18),
	(9781408855652, 'Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 'Fantasy', 'The first installment in the Harry Potter series, where a young boy discovers he is a wizard.', 15.00, 30),
	(9781594138577, 'Paper Towns', 'John Green', 'Young Adult', 'A coming-of-age story that explores friendship, love, and the search for identity.', 16.95, 20),
	(9781338878936, 'Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 'The second book in the Harry Potter series, full of magic, mystery, and adventure.', 16.95, 45),
	(9780735211292, 'Atomic Habits', 'James Clear', 'Self-Help', 'A practical guide on how to build good habits, break bad ones, and master the tiny behaviors that lead to remarkable results.', 36.00, 12),
	(9780545227247, 'Catching Fire', 'Suzanne Collins', 'Dystopian', 'The second installment in The Hunger Games series, where the stakes are higher and the action even more intense.', 15.99, 35);


-- Sample Data for Review
INSERT INTO Review (ReviewID, Rating, ReviewText, Date, CustomerID, ISBN) VALUES
	(301, 5, 'Absolutely gripping from start to finish! The world-building and characters are incredible.', '2025-10-15', 1234, 9781408855652),
	(302, 4, 'A heartwarming and beautifully written classic. The sisters feel so real and relatable.', '2025-10-20', 5678, 9780147514011),
	(303, 5, 'A masterpiece that stays with you long after reading. A must-read for everyone.', '2025-10-25', 9101, 9780439023528),
	(304, 3, 'Interesting mystery but a bit slow in the middle. Still worth reading for the ending.', '2025-11-02', 1213, 9781594138577),
	(305, 4, 'Great sequel with even more action and tension. Can''t wait for the next one!', '2025-11-05', 1234, 9780545227247),
	(306, 5, 'Absolutely loved the magical world and character development. Rowling never disappoints!', '2025-11-06', 5678, 9781338878936);


-- Sample Data for Purchase
INSERT INTO Purchase (PurchaseID, PurchaseDate, TotalPrice, CustomerID) VALUES
	(4001, '2025-10-12', 19.99, 1234),
	(4002, '2025-10-18', 49.00, 5678),
	(4003, '2025-10-25', 15.00, 9101),
	(4004, '2025-11-01', 16.95, 1213),
	(4005, '2025-11-07', 32.94, 1234),
	(4006, '2025-11-08', 108.00, 5678),
	(4007, '2025-11-09', 15.00, 9101);


-- Sample Data for PurchaseItem
INSERT INTO PurchaseItem (PurchaseID, ISBN, Quantity) VALUES
	(4001, 9780439023528, 1),  -- The Hunger Games
	(4002, 9780147514011, 2),  -- Little Women
	(4003, 9781408855652, 1),  -- Harry Potter 1
	(4004, 9781594138577, 1),  -- Paper Towns
	(4005, 9780545227247, 1),  -- Catching Fire
	(4005, 9781594138577, 1),  -- Paper Towns
	(4006, 9781338878936, 2),  -- Harry Potter 2
	(4007, 9780735211292, 3),  -- Atomic Habits
    (4007, 9781408855652, 1);  -- Harry Potter 1