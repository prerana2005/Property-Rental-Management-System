-- ===========================
-- 1) Create database + use
-- ===========================
CREATE DATABASE IF NOT EXISTS `rental_db`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
USE `rental_db`;

-- ===========================
-- 2) Drop existing tables
-- ===========================
DROP TABLE IF EXISTS `Assignment`;
DROP TABLE IF EXISTS `Payment`;
DROP TABLE IF EXISTS `RentalAgreement`;
DROP TABLE IF EXISTS `MaintenanceRequest`;
DROP TABLE IF EXISTS `House`;
DROP TABLE IF EXISTS `Employee`;
DROP TABLE IF EXISTS `Tenant`;
DROP TABLE IF EXISTS `Owner`;

-- ===========================
-- 3) Create tables (DDL)
-- Note: InnoDB for FK support, utf8mb4 charset
-- ===========================

-- Owner table
CREATE TABLE `Owner` (
  `OwnerID` INT NOT NULL AUTO_INCREMENT,
  `FullName` VARCHAR(100) NOT NULL,
  `Phone` VARCHAR(20),
  `Email` VARCHAR(150) UNIQUE,
  `Address` VARCHAR(255),
  PRIMARY KEY (`OwnerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tenant table
CREATE TABLE `Tenant` (
  `TenantID` INT NOT NULL AUTO_INCREMENT,
  `FullName` VARCHAR(100) NOT NULL,
  `Phone` VARCHAR(20),
  `Email` VARCHAR(150) UNIQUE,
  `Occupation` VARCHAR(100),
  `Address` VARCHAR(255),
  `ProofID` VARCHAR(50),
  PRIMARY KEY (`TenantID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Employee table
CREATE TABLE `Employee` (
  `EmployeeID` INT NOT NULL AUTO_INCREMENT,
  `FullName` VARCHAR(100) NOT NULL,
  `Role` VARCHAR(50),
  `Phone` VARCHAR(20),
  `Email` VARCHAR(150) UNIQUE,
  PRIMARY KEY (`EmployeeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- House table (FK -> Owner)
CREATE TABLE `House` (
  `HouseID` INT NOT NULL AUTO_INCREMENT,
  `OwnerID` INT NOT NULL,
  `Address` VARCHAR(255),
  `City` VARCHAR(100),
  `Type` VARCHAR(50),
  `RentAmount` DECIMAL(10,2) DEFAULT 0.00,
  `Status` ENUM('Available','Rented','Maintenance','Reserved') DEFAULT 'Available',
  `Furnishing` VARCHAR(50),
  PRIMARY KEY (`HouseID`),
  INDEX `idx_house_owner` (`OwnerID`),
  CONSTRAINT `fk_house_owner` FOREIGN KEY (`OwnerID`) REFERENCES `Owner`(`OwnerID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- RentalAgreement table (FK -> House, Tenant)
CREATE TABLE `RentalAgreement` (
  `AgreementID` INT NOT NULL AUTO_INCREMENT,
  `HouseID` INT NOT NULL,
  `TenantID` INT NOT NULL,
  `StartDate` DATE,
  `EndDate` DATE,
  `MonthlyRent` DECIMAL(10,2) NOT NULL,
  `SecurityDeposit` DECIMAL(10,2),
  `AgreementStatus` ENUM('Pending','Active','Terminated') DEFAULT 'Pending',
  PRIMARY KEY (`AgreementID`),
  INDEX `idx_ra_house` (`HouseID`),
  INDEX `idx_ra_tenant` (`TenantID`),
  CONSTRAINT `fk_ra_house` FOREIGN KEY (`HouseID`) REFERENCES `House`(`HouseID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ra_tenant` FOREIGN KEY (`TenantID`) REFERENCES `Tenant`(`TenantID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MaintenanceRequest (FK -> House, Tenant)
CREATE TABLE `MaintenanceRequest` (
  `RequestID` INT NOT NULL AUTO_INCREMENT,
  `HouseID` INT NOT NULL,
  `TenantID` INT NOT NULL,
  `RequestDate` DATE,
  `Description` TEXT,
  `Status` ENUM('Open','InProgress','Closed','Cancelled') DEFAULT 'Open',
  `Cost` DECIMAL(10,2),
  PRIMARY KEY (`RequestID`),
  INDEX `idx_mr_house` (`HouseID`),
  INDEX `idx_mr_tenant` (`TenantID`),
  CONSTRAINT `fk_mr_house` FOREIGN KEY (`HouseID`) REFERENCES `House`(`HouseID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_mr_tenant` FOREIGN KEY (`TenantID`) REFERENCES `Tenant`(`TenantID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Payment table (Tenant -> Owner)
CREATE TABLE `Payment` (
  `PaymentID` INT NOT NULL AUTO_INCREMENT,
  `TenantID` INT NOT NULL,
  `OwnerID` INT NOT NULL,
  `PaymentDate` DATE,
  `Amount` DECIMAL(10,2) NOT NULL,
  `Mode` ENUM('Cash','Card','BankTransfer','UPI','Cheque','Other') DEFAULT 'UPI',
  `Status` ENUM('Completed','Pending','Failed','Refunded') DEFAULT 'Completed',
  PRIMARY KEY (`PaymentID`),
  INDEX `idx_payment_tenant` (`TenantID`),
  INDEX `idx_payment_owner` (`OwnerID`),
  CONSTRAINT `fk_payment_tenant` FOREIGN KEY (`TenantID`) REFERENCES `Tenant`(`TenantID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_payment_owner` FOREIGN KEY (`OwnerID`) REFERENCES `Owner`(`OwnerID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Assignment table to implement the Assigned_To relationship (Employee <-> MaintenanceRequest)
-- Relationship has attributes (AssignedDate, CompletionDate) so it becomes a table
CREATE TABLE `Assignment` (
  `AssignmentID` INT NOT NULL AUTO_INCREMENT,
  `EmployeeID` INT NOT NULL,
  `RequestID` INT NOT NULL,
  `AssignedDate` DATE,
  `CompletionDate` DATE,
  PRIMARY KEY (`AssignmentID`),
  INDEX `idx_assign_emp` (`EmployeeID`),
  INDEX `idx_assign_req` (`RequestID`),
  CONSTRAINT `fk_assign_emp` FOREIGN KEY (`EmployeeID`) REFERENCES `Employee`(`EmployeeID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_assign_req` FOREIGN KEY (`RequestID`) REFERENCES `MaintenanceRequest`(`RequestID`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ===========================
-- 4) Show table structure (DESC) right after creation
-- ===========================
DESC `Owner`;
DESC `Tenant`;
DESC `Employee`;
DESC `House`;
DESC `RentalAgreement`;
DESC `MaintenanceRequest`;
DESC `Payment`;
DESC `Assignment`;

-- Also list all tables
SHOW TABLES;

-- ===========================
-- 5) Insert sample data (DML) - 10+ entries per table
-- ===========================

-- Owners (10 entries)
INSERT INTO `Owner` (`OwnerID`, `FullName`, `Phone`, `Email`, `Address`) VALUES
  (1, 'Ravi Kumar', '9876543210', 'ravi.kumar@example.com', '12 MG Road, Bangalore'),
  (2, 'Priya Sharma', '9876501234', 'priya.sharma@example.com', '45 Residency, Chennai'),
  (3, 'Suresh Rao', '9445556677', 'suresh.rao@example.com', '8 Park St, Hyderabad'),
  (4, 'Anjali Mehta', '9887766554', 'anjali.mehta@example.com', '23 Green Valley, Mumbai'),
  (5, 'Vikram Singh', '9776655443', 'vikram.singh@example.com', '67 Hill Road, Pune'),
  (6, 'Geeta Patel', '9665544332', 'geeta.patel@example.com', '89 Lake View, Delhi'),
  (7, 'Rajesh Nair', '9554433221', 'rajesh.nair@example.com', '34 Orchid Ave, Kolkata'),
  (8, 'Sunil Reddy', '9443322110', 'sunil.reddy@example.com', '56 Palm Street, Ahmedabad'),
  (9, 'Meera Joshi', '9332211009', 'meera.joshi@example.com', '78 Rose Lane, Surat'),
  (10, 'Arun Malhotra', '9221100998', 'arun.malhotra@example.com', '90 Sunset Blvd, Jaipur');

-- Tenants (10 entries)
INSERT INTO `Tenant` (`TenantID`, `FullName`, `Phone`, `Email`, `Occupation`, `Address`, `ProofID`) VALUES
  (1, 'Amit Shah', '9988776655', 'amit.shah@example.com', 'Software Engineer', 'Flat 101, Tower A', 'ID1001'),
  (2, 'Neha Gupta', '9876612345', 'neha.gupta@example.com', 'Research Scientist', 'Flat 202, Tower B', 'ID1002'),
  (3, 'Rohan Verma', '9900099000', 'rohan.verma@example.com', 'Student', 'PG House, 5th Cross', 'ID1003'),
  (4, 'Sneha Iyer', '9900112233', 'sneha.iyer@example.com', 'Graphic Designer', 'Flat 404, Tower C', 'ID1004'),
  (5, 'Karan Malhotra', '9811223344', 'karan.malhotra@example.com', 'Marketing Manager', 'Flat 505, Tower D', 'ID1005'),
  (6, 'Priya Reddy', '9722334455', 'priya.reddy@example.com', 'Doctor', 'Flat 606, Tower E', 'ID1006'),
  (7, 'Rahul Desai', '9633445566', 'rahul.desai@example.com', 'Accountant', 'Flat 707, Tower F', 'ID1007'),
  (8, 'Anita Choudhary', '9544556677', 'anita.choudhary@example.com', 'Teacher', 'Flat 808, Tower G', 'ID1008'),
  (9, 'Vishal Kapoor', '9455667788', 'vishal.kapoor@example.com', 'Business Analyst', 'Flat 909, Tower H', 'ID1009'),
  (10, 'Pooja Mehta', '9366778899', 'pooja.mehta@example.com', 'Architect', 'Flat 1010, Tower I', 'ID1010');

-- Employees (10 entries)
INSERT INTO `Employee` (`EmployeeID`, `FullName`, `Role`, `Phone`, `Email`) VALUES
  (1, 'Manoj Das', 'Plumber', '9441112233', 'manoj.das@services.com'),
  (2, 'Kavita Roy', 'Electrician', '9442223344', 'kavita.roy@services.com'),
  (3, 'Sajan K', 'Carpenter', '9443334455', 'sajan.k@services.com'),
  (4, 'Ramesh Kumar', 'Painter', '9444445566', 'ramesh.kumar@services.com'),
  (5, 'Laxmi Nair', 'Cleaner', '9445556677', 'laxmi.nair@services.com'),
  (6, 'Deepak Sharma', 'AC Technician', '9446667788', 'deepak.sharma@services.com'),
  (7, 'Anil Gupta', 'Security', '9447778899', 'anil.gupta@services.com'),
  (8, 'Sunita Patel', 'Gardener', '9448889900', 'sunita.patel@services.com'),
  (9, 'Rajiv Menon', 'Plumber', '9449990011', 'rajiv.menon@services.com'),
  (10, 'Madhavi Rao', 'Electrician', '9440001122', 'madhavi.rao@services.com');

-- Houses (12 entries - multiple houses per owner)
INSERT INTO `House` (`HouseID`, `OwnerID`, `Address`, `City`, `Type`, `RentAmount`, `Status`, `Furnishing`) VALUES
  (101, 1, '12 MG Road Apt 3B', 'Bangalore', 'Apartment', 25000.00, 'Available', 'Semi-Furnished'),
  (102, 1, '78 Park Lane', 'Bangalore', 'Independent', 35000.00, 'Rented', 'Furnished'),
  (103, 1, '45 Koramangala Rd', 'Bangalore', 'Villa', 55000.00, 'Available', 'Fully-Furnished'),
  (201, 2, '45 Residency Apt 5C', 'Chennai', 'Apartment', 18000.00, 'Rented', 'Unfurnished'),
  (202, 2, '23 Anna Nagar', 'Chennai', 'Apartment', 22000.00, 'Available', 'Semi-Furnished'),
  (301, 3, '8 Park St Apt 2A', 'Hyderabad', 'Apartment', 20000.00, 'Rented', 'Furnished'),
  (302, 3, '67 Jubilee Hills', 'Hyderabad', 'Independent', 40000.00, 'Maintenance', 'Fully-Furnished'),
  (401, 4, '23 Green Valley', 'Mumbai', 'Apartment', 45000.00, 'Rented', 'Semi-Furnished'),
  (501, 5, '67 Hill Road', 'Pune', 'Apartment', 28000.00, 'Available', 'Furnished'),
  (601, 6, '89 Lake View', 'Delhi', 'Independent', 38000.00, 'Rented', 'Fully-Furnished'),
  (701, 7, '34 Orchid Ave', 'Kolkata', 'Apartment', 15000.00, 'Available', 'Unfurnished'),
  (801, 8, '56 Palm Street', 'Ahmedabad', 'Apartment', 12000.00, 'Rented', 'Semi-Furnished');

-- RentalAgreements (10 entries)
INSERT INTO `RentalAgreement` (`AgreementID`, `HouseID`, `TenantID`, `StartDate`, `EndDate`, `MonthlyRent`, `SecurityDeposit`, `AgreementStatus`) VALUES
  (1001, 102, 1, '2024-07-01', '2025-06-30', 35000.00, 70000.00, 'Active'),
  (1002, 101, 3, '2025-01-01', '2025-12-31', 25000.00, 50000.00, 'Pending'),
  (1003, 201, 2, '2024-10-01', '2025-09-30', 18000.00, 36000.00, 'Active'),
  (1004, 301, 4, '2024-09-01', '2025-08-31', 20000.00, 40000.00, 'Active'),
  (1005, 401, 5, '2024-08-01', '2025-07-31', 45000.00, 90000.00, 'Active'),
  (1006, 601, 6, '2024-11-01', '2025-10-31', 38000.00, 76000.00, 'Active'),
  (1007, 801, 7, '2024-12-01', '2025-11-30', 12000.00, 24000.00, 'Active'),
  (1008, 302, 8, '2024-06-01', '2025-05-31', 40000.00, 80000.00, 'Terminated'),
  (1009, 103, 9, '2025-02-01', '2026-01-31', 55000.00, 110000.00, 'Pending'),
  (1010, 202, 10, '2024-07-15', '2025-07-14', 22000.00, 44000.00, 'Active');

-- MaintenanceRequests (12 entries)
INSERT INTO `MaintenanceRequest` (`RequestID`, `HouseID`, `TenantID`, `RequestDate`, `Description`, `Status`, `Cost`) VALUES
  (2001, 102, 1, '2024-08-05', 'Leaking pipe in bathroom', 'Closed', 1500.00),
  (2002, 101, 3, '2025-02-10', 'AC not cooling', 'InProgress', 500.00),
  (2003, 201, 2, '2024-11-20', 'Window grill repair', 'Closed', 1200.00),
  (2004, 301, 4, '2024-09-15', 'Kitchen sink blockage', 'Closed', 800.00),
  (2005, 401, 5, '2024-08-20', 'Electrical wiring issue', 'Closed', 2500.00),
  (2006, 601, 6, '2024-11-25', 'Painting required', 'Open', NULL),
  (2007, 801, 7, '2024-12-10', 'Door lock replacement', 'Closed', 600.00),
  (2008, 302, 8, '2024-07-01', 'Water heater not working', 'Closed', 1800.00),
  (2009, 103, 9, '2025-02-15', 'Furniture repair needed', 'Open', NULL),
  (2010, 202, 10, '2024-08-01', 'Carpet cleaning required', 'Closed', 400.00),
  (2011, 102, 1, '2024-09-10', 'Balcony railing loose', 'Closed', 900.00),
  (2012, 301, 4, '2024-10-05', 'Toilet flush repair', 'Closed', 700.00);

-- Payments (15 entries - multiple payments per tenant)
INSERT INTO `Payment` (`PaymentID`, `TenantID`, `OwnerID`, `PaymentDate`, `Amount`, `Mode`, `Status`) VALUES
  (3001, 1, 1, '2024-07-05', 35000.00, 'UPI', 'Completed'),
  (3002, 3, 1, '2025-01-05', 25000.00, 'BankTransfer', 'Completed'),
  (3003, 2, 2, '2024-10-05', 18000.00, 'Card', 'Completed'),
  (3004, 4, 3, '2024-09-05', 20000.00, 'UPI', 'Completed'),
  (3005, 5, 4, '2024-08-05', 45000.00, 'BankTransfer', 'Completed'),
  (3006, 6, 6, '2024-11-05', 38000.00, 'UPI', 'Completed'),
  (3007, 7, 8, '2024-12-05', 12000.00, 'Cash', 'Completed'),
  (3008, 8, 3, '2024-06-05', 40000.00, 'Card', 'Completed'),
  (3009, 10, 2, '2024-07-20', 22000.00, 'UPI', 'Completed'),
  (3010, 1, 1, '2024-08-05', 35000.00, 'UPI', 'Completed'),
  (3011, 2, 2, '2024-11-05', 18000.00, 'BankTransfer', 'Completed'),
  (3012, 4, 3, '2024-10-05', 20000.00, 'UPI', 'Completed'),
  (3013, 5, 4, '2024-09-05', 45000.00, 'Card', 'Completed'),
  (3014, 6, 6, '2024-12-05', 38000.00, 'UPI', 'Pending'),
  (3015, 7, 8, '2025-01-05', 12000.00, 'Cash', 'Completed');

-- Assignments (12 entries - one for each maintenance request)
INSERT INTO `Assignment` (`AssignmentID`, `EmployeeID`, `RequestID`, `AssignedDate`, `CompletionDate`) VALUES
  (4001, 1, 2001, '2024-08-06', '2024-08-07'),
  (4002, 6, 2002, '2025-02-11', NULL),
  (4003, 3, 2003, '2024-11-21', '2024-11-22'),
  (4004, 1, 2004, '2024-09-16', '2024-09-16'),
  (4005, 2, 2005, '2024-08-21', '2024-08-22'),
  (4006, 4, 2006, '2024-11-26', NULL),
  (4007, 3, 2007, '2024-12-11', '2024-12-12'),
  (4008, 9, 2008, '2024-07-02', '2024-07-03'),
  (4009, 3, 2009, '2025-02-16', NULL),
  (4010, 5, 2010, '2024-08-02', '2024-08-02'),
  (4011, 3, 2011, '2024-09-11', '2024-09-12'),
  (4012, 1, 2012, '2024-10-06', '2024-10-06');

-- ===========================
-- 6) Show contents after sample inserts
-- ===========================
DESC `Owner`;
SELECT * FROM `Owner`;

DESC `Tenant`;
SELECT * FROM `Tenant`;

DESC `Employee`;
SELECT * FROM `Employee`;

DESC `House`;
SELECT * FROM `House`;

DESC `RentalAgreement`;
SELECT * FROM `RentalAgreement`;

DESC `MaintenanceRequest`;
SELECT * FROM `MaintenanceRequest`;

DESC `Payment`;
SELECT * FROM `Payment`;

DESC `Assignment`;
SELECT * FROM `Assignment`;

-- ===========================
-- 7) CRUD examples 
-- ===========================

-- CREATE: 
SELECT * FROM `Tenant`;
INSERT INTO `Tenant` (`TenantID`, `FullName`, `Phone`, `Email`, `Occupation`, `Address`, `ProofID`)
  VALUES (11, 'Rahul Khanna', '9277886699', 'rahul.khanna@example.com', 'Data Scientist', 'Flat 1111, Tower J', 'ID1011');
SELECT * FROM `Tenant`;

-- READ: Show all tenants
SELECT * FROM Tenant;

-- UPDATE:
SELECT TenantID, FullName, Phone FROM `Tenant` WHERE TenantID = 11;
UPDATE `Tenant` SET Phone = '9887766554' WHERE TenantID = 11;
SELECT TenantID, FullName, Phone FROM `Tenant` WHERE TenantID = 11;

-- DELETE:
SELECT * FROM `Payment` WHERE PaymentID = 3014;
DELETE FROM `Payment` WHERE `PaymentID` = 3014;
SELECT * FROM `Payment` WHERE PaymentID = 3014;

-- ===========================
-- 8) JOIN queries demonstrating relationships
-- ===========================
-- Agreements + Tenant + House
SELECT ra.AgreementID, ra.StartDate, ra.EndDate, ra.MonthlyRent,
       t.TenantID, t.FullName AS TenantName,
       h.HouseID, h.Address AS HouseAddress, h.City
FROM `RentalAgreement` ra
JOIN `Tenant` t ON ra.TenantID = t.TenantID
JOIN `House` h ON ra.HouseID = h.HouseID;

-- Which payments did OwnerID = 1 receive?
SELECT p.PaymentID, p.PaymentDate, p.Amount, t.FullName AS Payer
FROM `Payment` p
JOIN `Tenant` t ON p.TenantID = t.TenantID
WHERE p.OwnerID = 1;

-- Maintenance requests with assigned employee(s)
SELECT mr.RequestID, mr.Description, mr.Status, mr.Cost,
       a.AssignmentID, e.EmployeeID, e.FullName AS EmployeeName, e.Role,
       a.AssignedDate, a.CompletionDate
FROM `MaintenanceRequest` mr
LEFT JOIN `Assignment` a ON mr.RequestID = a.RequestID
LEFT JOIN `Employee` e ON a.EmployeeID = e.EmployeeID;

-- Houses with their owners
SELECT h.HouseID, h.Address, h.City, h.RentAmount, h.Status,
       o.OwnerID, o.FullName AS OwnerName, o.Phone AS OwnerPhone
FROM `House` h
JOIN `Owner` o ON h.OwnerID = o.OwnerID;

-- ===========================
-- 9) ALTER table 
-- ===========================
DESC `Tenant`;
ALTER TABLE `Tenant` ADD COLUMN `IsActive` TINYINT(1) NOT NULL DEFAULT 1;
DESC `Tenant`;
SELECT TenantID, FullName, IsActive FROM `Tenant` LIMIT 5;

-- ===========================
-- 10) Foreign key enforcement check
-- ===========================
-- The following is expected to FAIL because OwnerID 9999 does not exist.
-- uncomment and run
-- INSERT INTO `House` (`HouseID`, `OwnerID`, `Address`, `City`) VALUES (999, 9999, 'Nowhere Road', 'Nowhere');

-- ===========================
-- 11) Additional analytical queries
-- ===========================

-- Total rent collected by each owner
SELECT o.OwnerID, o.FullName AS OwnerName, 
       COUNT(p.PaymentID) AS TotalPayments,
       SUM(p.Amount) AS TotalRentCollected
FROM `Owner` o
LEFT JOIN `Payment` p ON o.OwnerID = p.OwnerID
WHERE p.Status = 'Completed'
GROUP BY o.OwnerID, o.FullName
ORDER BY TotalRentCollected DESC;

-- Maintenance cost by house
SELECT h.HouseID, h.Address, 
       COUNT(mr.RequestID) AS TotalRequests,
       SUM(COALESCE(mr.Cost, 0)) AS TotalMaintenanceCost
FROM `House` h
LEFT JOIN `MaintenanceRequest` mr ON h.HouseID = mr.HouseID
GROUP BY h.HouseID, h.Address
ORDER BY TotalMaintenanceCost DESC;

-- Employee performance (completed assignments)
SELECT e.EmployeeID, e.FullName, e.Role,
       COUNT(a.AssignmentID) AS TotalAssignments,
       COUNT(CASE WHEN a.CompletionDate IS NOT NULL THEN 1 END) AS CompletedAssignments
FROM `Employee` e
LEFT JOIN `Assignment` a ON e.EmployeeID = a.EmployeeID
GROUP BY e.EmployeeID, e.FullName, e.Role
ORDER BY CompletedAssignments DESC;

-- Available houses by city
SELECT City, 
       COUNT(*) AS TotalHouses,
       COUNT(CASE WHEN Status = 'Available' THEN 1 END) AS AvailableHouses
FROM `House`
GROUP BY City
ORDER BY AvailableHouses DESC;



-- ===========================
-- FUNCTIONS 
-- ===========================

-- Function 1: Calculate total revenue for an owner
DELIMITER //
CREATE FUNCTION CalculateOwnerRevenue(owner_id INT) 
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE total_revenue DECIMAL(10,2) DEFAULT 0;
    
    SELECT COALESCE(SUM(Amount), 0) INTO total_revenue
    FROM Payment 
    WHERE OwnerID = owner_id 
    AND Status = 'Completed';
    
    RETURN total_revenue;
END //
DELIMITER ;

-- Function 2: Calculate average maintenance cost for a house
DELIMITER //
CREATE FUNCTION GetAverageMaintenanceCost(house_id INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE avg_cost DECIMAL(10,2);
    
    SELECT COALESCE(AVG(Cost), 0) INTO avg_cost
    FROM MaintenanceRequest
    WHERE HouseID = house_id 
    AND Cost IS NOT NULL;
    
    RETURN avg_cost;
END //
DELIMITER ;

-- Function 3: Check if house is available for rent
DELIMITER //
CREATE FUNCTION IsHouseAvailable(house_id INT)
RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE house_status VARCHAR(20);
    
    SELECT Status INTO house_status
    FROM House 
    WHERE HouseID = house_id;
    
    RETURN (house_status = 'Available');
END //
DELIMITER ;

-- Function 4: Get tenant's current active agreement
DELIMITER //
CREATE FUNCTION GetTenantActiveAgreement(tenant_id INT)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE active_agreement_id INT;
    
    SELECT AgreementID INTO active_agreement_id
    FROM RentalAgreement
    WHERE TenantID = tenant_id 
    AND AgreementStatus = 'Active'
    AND CURDATE() BETWEEN StartDate AND EndDate
    LIMIT 1;
    
    RETURN active_agreement_id;
END //
DELIMITER ;

-- Function 5: Calculate total maintenance cost for a house
DELIMITER //
CREATE FUNCTION GetTotalMaintenanceCost(house_id INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE total_cost DECIMAL(10,2);
    
    SELECT COALESCE(SUM(Cost), 0) INTO total_cost
    FROM MaintenanceRequest
    WHERE HouseID = house_id 
    AND Cost IS NOT NULL;
    
    RETURN total_cost;
END //
DELIMITER ;

-- Function 6: Get number of active agreements for an owner
DELIMITER //
CREATE FUNCTION CountOwnerActiveAgreements(owner_id INT)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE active_count INT;
    
    SELECT COUNT(*) INTO active_count
    FROM RentalAgreement ra
    JOIN House h ON ra.HouseID = h.HouseID
    WHERE h.OwnerID = owner_id
    AND ra.AgreementStatus = 'Active'
    AND CURDATE() BETWEEN ra.StartDate AND ra.EndDate;
    
    RETURN active_count;
END //
DELIMITER ;

-- Function 7: Calculate security deposit amount based on monthly rent
DELIMITER //
CREATE FUNCTION CalculateSecurityDeposit(monthly_rent DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN monthly_rent * 2; -- Typically 2 months rent as security deposit
END //
DELIMITER ;

-- Function 8: Check if tenant has overdue payments
DELIMITER //
CREATE FUNCTION HasOverduePayments(tenant_id INT)
RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE overdue_count INT;
    
    SELECT COUNT(*) INTO overdue_count
    FROM Payment p
    JOIN RentalAgreement ra ON p.TenantID = ra.TenantID
    WHERE p.TenantID = tenant_id
    AND p.Status = 'Pending'
    AND p.PaymentDate < CURDATE() - INTERVAL 7 DAY; -- Overdue if pending for more than 7 days
    
    RETURN (overdue_count > 0);
END //
DELIMITER ;


-- ===========================
-- TEST THE FUNCTIONS
-- ===========================

-- Test Function 1: Calculate owner revenue
SELECT OwnerID, FullName, CalculateOwnerRevenue(OwnerID) AS TotalRevenue
FROM Owner;

-- Test Function 2: Average maintenance cost per house
SELECT HouseID, Address, GetAverageMaintenanceCost(HouseID) AS AvgMaintenanceCost
FROM House;

-- Test Function 3: Check house availability
SELECT HouseID, Address, Status, IsHouseAvailable(HouseID) AS IsAvailable
FROM House;

-- Test Function 4: Get tenant's active agreement
SELECT TenantID, FullName, GetTenantActiveAgreement(TenantID) AS ActiveAgreementID
FROM Tenant;

-- Test Function 5: Total maintenance cost per house
SELECT HouseID, Address, GetTotalMaintenanceCost(HouseID) AS TotalMaintenanceCost
FROM House;

-- Test Function 6: Count active agreements per owner
SELECT OwnerID, FullName, CountOwnerActiveAgreements(OwnerID) AS ActiveAgreements
FROM Owner;

-- Test Function 7: Calculate security deposit
SELECT 25000.00 AS MonthlyRent, CalculateSecurityDeposit(25000.00) AS SecurityDeposit;

-- Test Function 8: Check for overdue payments
SELECT TenantID, FullName, HasOverduePayments(TenantID) AS HasOverduePayments
FROM Tenant;

-- Complex query using multiple functions
SELECT 
    h.HouseID,
    h.Address,
    h.RentAmount,
    IsHouseAvailable(h.HouseID) AS Available,
    GetAverageMaintenanceCost(h.HouseID) AS AvgMaintenanceCost,
    GetTotalMaintenanceCost(h.HouseID) AS TotalMaintenanceCost
FROM House h
WHERE GetTotalMaintenanceCost(h.HouseID) > 0;

-- Nested query with function calls
SELECT 
    o.OwnerID,
    o.FullName AS OwnerName,
    CalculateOwnerRevenue(o.OwnerID) AS TotalRevenue,
    CountOwnerActiveAgreements(o.OwnerID) AS ActiveAgreements,
    (SELECT COUNT(*) FROM House h WHERE h.OwnerID = o.OwnerID) AS TotalProperties
FROM Owner o
ORDER BY TotalRevenue DESC;


-- ===========================
-- USER MANAGEMENT - THREE ROLES
-- ===========================

-- 1. TENANT USER (Can view their data and create maintenance requests)
CREATE USER 'tenant_user'@'localhost' IDENTIFIED BY 'tenant123';

GRANT SELECT ON rental_db.Tenant TO 'tenant_user'@'localhost';
GRANT SELECT ON rental_db.House TO 'tenant_user'@'localhost';
GRANT SELECT ON rental_db.RentalAgreement TO 'tenant_user'@'localhost';
GRANT SELECT ON rental_db.Payment TO 'tenant_user'@'localhost';
GRANT SELECT, INSERT ON rental_db.MaintenanceRequest TO 'tenant_user'@'localhost';
GRANT SELECT ON rental_db.Assignment TO 'tenant_user'@'localhost';
GRANT SELECT ON rental_db.Employee TO 'tenant_user'@'localhost';

-- Specific column-level permissions for privacy
REVOKE ALL PRIVILEGES ON rental_db.Tenant FROM 'tenant_user'@'localhost';
GRANT SELECT (TenantID, FullName, Phone, Email, Occupation) ON rental_db.Tenant TO 'tenant_user'@'localhost';

-- 2. OWNER USER (Can view their properties, agreements, and payments)
CREATE USER 'owner_user'@'localhost' IDENTIFIED BY 'owner123';

GRANT SELECT ON rental_db.Owner TO 'owner_user'@'localhost';
GRANT SELECT ON rental_db.House TO 'owner_user'@'localhost';
GRANT SELECT ON rental_db.RentalAgreement TO 'owner_user'@'localhost';
GRANT SELECT ON rental_db.Payment TO 'owner_user'@'localhost';
GRANT SELECT ON rental_db.MaintenanceRequest TO 'owner_user'@'localhost';
GRANT SELECT ON rental_db.Tenant TO 'owner_user'@'localhost';

-- Column-level permissions for Tenant privacy
REVOKE ALL PRIVILEGES ON rental_db.Tenant FROM 'owner_user'@'localhost';
GRANT SELECT (TenantID, FullName, Phone, Email, Occupation) ON rental_db.Tenant TO 'owner_user'@'localhost';

-- 3. EMPLOYEE USER (Maintenance staff - can manage maintenance requests and assignments)
CREATE USER 'employee_user'@'localhost' IDENTIFIED BY 'employee123';

GRANT SELECT ON rental_db.Employee TO 'employee_user'@'localhost';
GRANT SELECT ON rental_db.MaintenanceRequest TO 'employee_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON rental_db.Assignment TO 'employee_user'@'localhost';
GRANT SELECT ON rental_db.House TO 'employee_user'@'localhost';
GRANT SELECT ON rental_db.Tenant TO 'employee_user'@'localhost';

-- Column-level permissions for privacy
REVOKE ALL PRIVILEGES ON rental_db.Tenant FROM 'employee_user'@'localhost';
GRANT SELECT (TenantID, FullName, Phone) ON rental_db.Tenant TO 'employee_user'@'localhost';

-- Execute permissions for functions (all users can use functions)
GRANT EXECUTE ON FUNCTION rental_db.CalculateOwnerRevenue TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CountOwnerActiveAgreements TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CalculateSecurityDeposit TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetAverageMaintenanceCost TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTenantActiveAgreement TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTotalMaintenanceCost TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.HasOverduePayments TO 'tenant_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.IsHouseAvailable TO 'tenant_user'@'localhost';

GRANT EXECUTE ON FUNCTION rental_db.CalculateOwnerRevenue TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CountOwnerActiveAgreements TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CalculateSecurityDeposit TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetAverageMaintenanceCost TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTenantActiveAgreement TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTotalMaintenanceCost TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.HasOverduePayments TO 'owner_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.IsHouseAvailable TO 'owner_user'@'localhost';

GRANT EXECUTE ON FUNCTION rental_db.CalculateOwnerRevenue TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CountOwnerActiveAgreements TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.CalculateSecurityDeposit TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetAverageMaintenanceCost TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTenantActiveAgreement TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.GetTotalMaintenanceCost TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.HasOverduePayments TO 'employee_user'@'localhost';
GRANT EXECUTE ON FUNCTION rental_db.IsHouseAvailable TO 'employee_user'@'localhost';
-- Apply all privileges
FLUSH PRIVILEGES;

-- ===========================
-- VERIFY USER CREATION AND PERMISSIONS
-- ===========================

-- Show all created users
SELECT user, host, authentication_string 
FROM mysql.user 
WHERE user IN ('tenant_user', 'owner_user', 'employee_user');

-- Show grants for each user
SHOW GRANTS FOR 'tenant_user'@'localhost';
SHOW GRANTS FOR 'owner_user'@'localhost';
SHOW GRANTS FOR 'employee_user'@'localhost';

-- ===========================
-- TRIGGERS SECTION
-- ===========================

-- Trigger 1: Auto-update House status when RentalAgreement becomes Active
DELIMITER //
CREATE TRIGGER UpdateHouseStatusOnAgreementActivation
AFTER UPDATE ON RentalAgreement
FOR EACH ROW
BEGIN
    IF NEW.AgreementStatus = 'Active' AND OLD.AgreementStatus != 'Active' THEN
        UPDATE House 
        SET Status = 'Rented' 
        WHERE HouseID = NEW.HouseID;
    END IF;
    
    IF NEW.AgreementStatus = 'Terminated' AND OLD.AgreementStatus != 'Terminated' THEN
        UPDATE House 
        SET Status = 'Available' 
        WHERE HouseID = NEW.HouseID;
    END IF;
END //
DELIMITER ;

-- Trigger 2: Auto-calculate Security Deposit when inserting RentalAgreement
DELIMITER //
CREATE TRIGGER CalculateSecurityDepositOnInsert
BEFORE INSERT ON RentalAgreement
FOR EACH ROW
BEGIN
    IF NEW.SecurityDeposit IS NULL THEN
        SET NEW.SecurityDeposit = NEW.MonthlyRent * 2;
    END IF;
END //
DELIMITER ;

-- Trigger 3: Log maintenance cost changes
CREATE TABLE MaintenanceCostAudit (
    AuditID INT AUTO_INCREMENT PRIMARY KEY,
    RequestID INT,
    OldCost DECIMAL(10,2),
    NewCost DECIMAL(10,2),
    ChangedBy VARCHAR(100),
    ChangeDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //
CREATE TRIGGER AuditMaintenanceCostChanges
AFTER UPDATE ON MaintenanceRequest
FOR EACH ROW
BEGIN
    IF OLD.Cost != NEW.Cost THEN
        INSERT INTO MaintenanceCostAudit (RequestID, OldCost, NewCost, ChangedBy)
        VALUES (NEW.RequestID, OLD.Cost, NEW.Cost, USER());
    END IF;
END //
DELIMITER ;

-- Trigger 4: Prevent duplicate active agreements for same house
DELIMITER //
CREATE TRIGGER PreventDuplicateActiveAgreements
BEFORE INSERT ON RentalAgreement
FOR EACH ROW
BEGIN
    DECLARE active_count INT;
    
    SELECT COUNT(*) INTO active_count
    FROM RentalAgreement
    WHERE HouseID = NEW.HouseID 
    AND AgreementStatus = 'Active'
    AND CURDATE() BETWEEN StartDate AND EndDate;
    
    IF active_count > 0 AND NEW.AgreementStatus = 'Active' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot create active agreement for a house that already has an active agreement';
    END IF;
END //
DELIMITER ;

-- ===========================
-- STORED PROCEDURES SECTION
-- ===========================

-- Procedure 1: Create new rental agreement with validation
DELIMITER //
CREATE PROCEDURE CreateRentalAgreement(
    IN p_HouseID INT,
    IN p_TenantID INT,
    IN p_StartDate DATE,
    IN p_EndDate DATE,
    IN p_MonthlyRent DECIMAL(10,2),
    IN p_SecurityDeposit DECIMAL(10,2)
)
BEGIN
    DECLARE house_status VARCHAR(20);
    DECLARE existing_agreement INT;
    
    -- Check if house exists and is available
    SELECT Status INTO house_status FROM House WHERE HouseID = p_HouseID;
    IF house_status != 'Available' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'House is not available for rent';
    END IF;
    
    -- Check for overlapping agreements
    SELECT COUNT(*) INTO existing_agreement
    FROM RentalAgreement
    WHERE HouseID = p_HouseID
    AND AgreementStatus = 'Active'
    AND (p_StartDate BETWEEN StartDate AND EndDate OR p_EndDate BETWEEN StartDate AND EndDate);
    
    IF existing_agreement > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'House has overlapping rental agreement';
    END IF;
    
    -- Insert the agreement
    INSERT INTO RentalAgreement (HouseID, TenantID, StartDate, EndDate, MonthlyRent, SecurityDeposit, AgreementStatus)
    VALUES (p_HouseID, p_TenantID, p_StartDate, p_EndDate, p_MonthlyRent, p_SecurityDeposit, 'Pending');
    
    SELECT LAST_INSERT_ID() AS NewAgreementID;
END //
DELIMITER ;

-- Procedure 2: Process monthly payment
DELIMITER //
CREATE PROCEDURE ProcessMonthlyPayment(
    IN p_TenantID INT,
    IN p_OwnerID INT,
    IN p_Amount DECIMAL(10,2),
    IN p_PaymentMode ENUM('Cash','Card','BankTransfer','UPI','Cheque','Other')
)
BEGIN
    DECLARE active_agreement INT;
    
    -- Check if tenant has active agreement
    SELECT AgreementID INTO active_agreement
    FROM RentalAgreement
    WHERE TenantID = p_TenantID 
    AND AgreementStatus = 'Active'
    AND CURDATE() BETWEEN StartDate AND EndDate;
    
    IF active_agreement IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tenant does not have an active rental agreement';
    END IF;
    
    -- Insert payment record
    INSERT INTO Payment (TenantID, OwnerID, PaymentDate, Amount, Mode, Status)
    VALUES (p_TenantID, p_OwnerID, CURDATE(), p_Amount, p_PaymentMode, 'Completed');
    
    SELECT LAST_INSERT_ID() AS PaymentID;
END //
DELIMITER ;

-- Procedure 3: Assign employee to maintenance request
DELIMITER //
CREATE PROCEDURE AssignMaintenanceEmployee(
    IN p_RequestID INT,
    IN p_EmployeeID INT
)
BEGIN
    DECLARE request_status VARCHAR(20);
    
    -- Check if request exists and is open
    SELECT Status INTO request_status 
    FROM MaintenanceRequest 
    WHERE RequestID = p_RequestID;
    
    IF request_status != 'Open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maintenance request is not open for assignment';
    END IF;
    
    -- Create assignment
    INSERT INTO Assignment (EmployeeID, RequestID, AssignedDate)
    VALUES (p_EmployeeID, p_RequestID, CURDATE());
    
    -- Update request status
    UPDATE MaintenanceRequest 
    SET Status = 'InProgress' 
    WHERE RequestID = p_RequestID;
    
    SELECT LAST_INSERT_ID() AS AssignmentID;
END //
DELIMITER ;

-- Procedure 4: Complete maintenance request
DELIMITER //
CREATE PROCEDURE CompleteMaintenanceRequest(
    IN p_RequestID INT,
    IN p_ActualCost DECIMAL(10,2)
)
BEGIN
    -- Update maintenance request
    UPDATE MaintenanceRequest 
    SET Status = 'Closed', Cost = p_ActualCost
    WHERE RequestID = p_RequestID;
    
    -- Update assignment completion date
    UPDATE Assignment 
    SET CompletionDate = CURDATE()
    WHERE RequestID = p_RequestID;
END //
DELIMITER ;

-- ===========================
-- NESTED QUERIES SECTION
-- ===========================

-- Nested Query 1: Find tenants who have paid more than average rent
SELECT t.TenantID, t.FullName, p.Amount
FROM Tenant t
JOIN Payment p ON t.TenantID = p.TenantID
WHERE p.Amount > (
    SELECT AVG(Amount) 
    FROM Payment 
    WHERE Status = 'Completed'
)
AND p.Status = 'Completed';

-- Nested Query 2: Find houses that have never had maintenance requests
SELECT h.HouseID, h.Address, h.City
FROM House h
WHERE h.HouseID NOT IN (
    SELECT DISTINCT HouseID 
    FROM MaintenanceRequest
);

-- Nested Query 3: Find owners with above average property count
SELECT o.OwnerID, o.FullName, 
       (SELECT COUNT(*) FROM House h WHERE h.OwnerID = o.OwnerID) AS PropertyCount
FROM Owner o
WHERE (SELECT COUNT(*) FROM House h WHERE h.OwnerID = o.OwnerID) > (
    SELECT AVG(prop_count) 
    FROM (
        SELECT COUNT(*) AS prop_count 
        FROM House 
        GROUP BY OwnerID
    ) AS avg_props
);

-- Nested Query 4: Find employees with highest completion rate
SELECT e.EmployeeID, e.FullName, e.Role,
       (SELECT COUNT(*) FROM Assignment a WHERE a.EmployeeID = e.EmployeeID) AS TotalAssignments,
       (SELECT COUNT(*) FROM Assignment a WHERE a.EmployeeID = e.EmployeeID AND a.CompletionDate IS NOT NULL) AS CompletedAssignments,
       ROUND(
           (SELECT COUNT(*) FROM Assignment a WHERE a.EmployeeID = e.EmployeeID AND a.CompletionDate IS NOT NULL) / 
           GREATEST((SELECT COUNT(*) FROM Assignment a WHERE a.EmployeeID = e.EmployeeID), 1) * 100, 2
       ) AS CompletionRate
FROM Employee e
ORDER BY CompletionRate DESC;

-- ===========================
-- ADDITIONAL AGGREGATE QUERIES
-- ===========================

-- Aggregate Query 1: Monthly revenue trend
SELECT 
    YEAR(PaymentDate) AS Year,
    MONTH(PaymentDate) AS Month,
    COUNT(*) AS TotalPayments,
    SUM(Amount) AS TotalRevenue,
    AVG(Amount) AS AveragePayment,
    MIN(Amount) AS MinPayment,
    MAX(Amount) AS MaxPayment
FROM Payment
WHERE Status = 'Completed'
GROUP BY YEAR(PaymentDate), MONTH(PaymentDate)
ORDER BY Year DESC, Month DESC;

-- Aggregate Query 2: Maintenance statistics by employee role
SELECT 
    e.Role,
    COUNT(DISTINCT a.EmployeeID) AS TotalEmployees,
    COUNT(a.AssignmentID) AS TotalAssignments,
    AVG(DATEDIFF(a.CompletionDate, a.AssignedDate)) AS AvgCompletionDays,
    SUM(mr.Cost) AS TotalMaintenanceCost,
    AVG(mr.Cost) AS AvgMaintenanceCost
FROM Employee e
LEFT JOIN Assignment a ON e.EmployeeID = a.EmployeeID
LEFT JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID
WHERE a.CompletionDate IS NOT NULL
GROUP BY e.Role
ORDER BY TotalAssignments DESC;

-- Aggregate Query 3: City-wise rental market analysis
SELECT 
    City,
    COUNT(*) AS TotalProperties,
    COUNT(CASE WHEN Status = 'Available' THEN 1 END) AS AvailableProperties,
    COUNT(CASE WHEN Status = 'Rented' THEN 1 END) AS RentedProperties,
    AVG(RentAmount) AS AverageRent,
    MIN(RentAmount) AS MinRent,
    MAX(RentAmount) AS MaxRent,
    SUM(RentAmount) AS TotalRentPotential
FROM House
GROUP BY City
ORDER BY AverageRent DESC;

-- Aggregate Query 4: Tenant payment behavior analysis
SELECT 
    t.TenantID,
    t.FullName,
    COUNT(p.PaymentID) AS TotalPayments,
    SUM(p.Amount) AS TotalPaid,
    AVG(p.Amount) AS AveragePayment,
    COUNT(CASE WHEN p.Status = 'Pending' THEN 1 END) AS PendingPayments,
    COUNT(CASE WHEN p.Status = 'Completed' THEN 1 END) AS CompletedPayments,
    DATEDIFF(MAX(p.PaymentDate), MIN(p.PaymentDate)) AS TenureDays
FROM Tenant t
LEFT JOIN Payment p ON t.TenantID = p.TenantID
GROUP BY t.TenantID, t.FullName
ORDER BY TotalPaid DESC;

-- ===========================
-- TEST TRIGGERS AND PROCEDURES
-- ===========================

-- Test Trigger 1: Update agreement status to activate house status change
SELECT * FROM House WHERE HouseID = 101;
UPDATE RentalAgreement SET AgreementStatus = 'Active' WHERE AgreementID = 1002;
SELECT * FROM House WHERE HouseID = 101;

-- Test Trigger 2: Insert rental agreement without security deposit
INSERT INTO RentalAgreement (HouseID, TenantID, StartDate, EndDate, MonthlyRent, AgreementStatus)
VALUES (501, 11, '2025-03-01', '2026-02-28', 28000.00, 'Pending');
SELECT * FROM RentalAgreement WHERE AgreementID = LAST_INSERT_ID();

-- Test Procedure 1: Create new rental agreement
CALL CreateRentalAgreement(701, 11, '2025-03-01', '2026-02-28', 15000.00, NULL);

-- Test Procedure 2: Process monthly payment
CALL ProcessMonthlyPayment(1, 1, 35000.00, 'UPI');

-- Test Procedure 3: Assign employee to maintenance
CALL AssignMaintenanceEmployee(2006, 4);

-- Test Procedure 4: Complete maintenance request
CALL CompleteMaintenanceRequest(2006, 3000.00);

-- Test nested queries
SELECT * FROM (
    SELECT HouseID, Address, RentAmount,
           RANK() OVER (ORDER BY RentAmount DESC) as RentRank
    FROM House
) AS ranked_houses
WHERE RentRank <= 3;

-- Test aggregate queries with HAVING clause
SELECT City, AVG(RentAmount) as AvgRent
FROM House
GROUP BY City
HAVING AVG(RentAmount) > 20000;

-- ===========================
-- FINAL DATABASE OVERVIEW
-- ===========================
SHOW TABLES;

-- Count records in each table
SELECT 
    'Owner' as Table_Name, COUNT(*) as Record_Count FROM Owner
UNION ALL
SELECT 'Tenant', COUNT(*) FROM Tenant
UNION ALL
SELECT 'Employee', COUNT(*) FROM Employee
UNION ALL
SELECT 'House', COUNT(*) FROM House
UNION ALL
SELECT 'RentalAgreement', COUNT(*) FROM RentalAgreement
UNION ALL
SELECT 'MaintenanceRequest', COUNT(*) FROM MaintenanceRequest
UNION ALL
SELECT 'Payment', COUNT(*) FROM Payment
UNION ALL
SELECT 'Assignment', COUNT(*) FROM Assignment
UNION ALL
SELECT 'MaintenanceCostAudit', COUNT(*) FROM MaintenanceCostAudit;

-- Show all created functions and procedures
SHOW FUNCTION STATUS WHERE Db = 'rental_db';
SHOW PROCEDURE STATUS WHERE Db = 'rental_db';
SHOW TRIGGERS FROM rental_db;