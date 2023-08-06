# contact-dbm
Database management/library for the Contact API.

DB Creation PSQL commands:

Creating rooms table:
    CREATE TABLE rooms (room_id VARCHAR(25)PRIMARY KEY, capacity INT NOT NULL, building_name VARCHAR(25) NOT NULL);

Creating people table:
    CREATE TABLE people (email VARCHAR(50)PRIMARY KEY, name VARCHAR(50) NOT NULL, student_id INT);

Creating scans table:
    CREATE TABLE scans (scan_id serial PRIMARY KEY,person_email VARCHAR(50) NOT NULL,scan_time TIMESTAMP NOT NULL,room_id VARCHAR(25) NOT NULL, FOREIGN KEY (room_id) REFERENCES rooms(room_id), FOREIGN KEY (person_email) REFERENCES people(email));
