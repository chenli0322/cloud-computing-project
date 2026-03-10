-- ArchNav MySQL Initialization Script
-- Creates the archemy database, user, and stored procedures

-- Create database
CREATE DATABASE IF NOT EXISTS archemy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'archemy'@'%' IDENTIFIED BY 'archemydb1960%';
GRANT ALL PRIVILEGES ON archemy.* TO 'archemy'@'%';
FLUSH PRIVILEGES;

USE archemy;

-- Stored procedures from procedures.sql
DELIMITER $$

CREATE PROCEDURE archemy.insert_into_kad(
    IN kad_name VARCHAR(100),
    IN kad_link VARCHAR(300),
    IN kad_public_link VARCHAR(300),
    IN domain_id INT(11),
    IN business_problem INTEGER,
    OUT kad_id INT(11)
)
BEGIN
    INSERT INTO kads(kad_name, domain_id, kad_link, kad_link_public, RECURRING_BUS_PROBLEM_ID)
    VALUES (kad_name, domain_id, kad_link, kad_public_link, business_problem);
    SELECT LAST_INSERT_ID() INTO kad_id;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE archemy.insert_into_kad_dim_area(
    IN in_kad_id INTEGER,
    IN in_area_id INTEGER,
    IN in_area_child_id INTEGER,
    IN in_dimension_id INTEGER
)
BEGIN
    INSERT INTO kad_dimensions_area(kad_id, dimension_id, area_id, area_parent_id)
    VALUES (in_kad_id, in_dimension_id, in_area_child_id, in_area_id);
END $$

DELIMITER ;
