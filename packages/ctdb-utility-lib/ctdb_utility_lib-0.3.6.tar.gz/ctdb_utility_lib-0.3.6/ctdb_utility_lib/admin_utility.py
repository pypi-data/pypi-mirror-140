from os import stat
from typing import Tuple
import psycopg2
import re
from datetime import datetime, timedelta
import sys


def connect_to_db():
    """
    Connects to the database and returns a connection object.
    """
    return psycopg2.connect(
        database="Contact_Tracing_DB",
        user="postgres",
        password="password",
        host="34.134.212.102",
    )

# check email format
def valid_email_format(email: str):
    regex = "^[A-Za-z0-9]+[\._]?[A-Za-z0-9]+[@]\w+[.]\w{2,3}$"

    return re.search(regex, email) != None

def _execute_statement(conn, statement):
    """
    Executes a PSQL statement with a given connection.

    Returns a cursor with the response of the statement.
    """
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()

    return cursor

#gets records for every scan made
def get_records(limit:int,conn):

    if(limit != 0):
        statement = f"SELECT * FROM scans ORDER BY scan_time LIMIT '{limit}'"
    else:
        statement = "SELECT * FROM scans" 
     
    #cursor
    cur = _execute_statement(conn, statement)
    
    #executing SQL statement failed
    if(cur == None):
        raise LookupError("Error occured while executing the SQL statement")
    
    #fetch query results
    result = cur.fetchall()

    if(len(result) == 0):
        return None
    
    cur.close()

    return result

#gets records for every scan made by a specific user
def get_user_records(email:str,limit:int,conn):

    if not valid_email_format(email):
        return -1
    
    if(limit != 0):
        statement = f"SELECT * FROM scans WHERE person_email = '{email}' ORDER BY scan_time LIMIT '{limit}'"
    else:
        statement = f"SELECT * FROM scans WHERE person_email = '{email}'"

    #cursor
    cur = _execute_statement(conn, statement)
    
    #executing SQL statement failed
    if(cur == None):
        raise LookupError("Error occured while executing the SQL statement")
    
    #fetch query results
    result = cur.fetchall()

    if(len(result) == 0):
        return None
    
    cur.close()

    return result

#get people who were in contact with the person reporting a positive covid test
def get_contacts(email:str,date:datetime,conn):

    #validate email format
    if not valid_email_format(email):
        return -1
    
    #validate that the passed in date is no more than 14 days before today's date
    if(datetime.now() - date > timedelta(days=14)):
        return -1 

    #query all the students the infected student has been in contact with in a classroom
    cur = _execute_statement(conn, f"""
        WITH rooms_attended AS(
            SELECT room_id,scan_time,x_pos,y_pos
            FROM scans
            WHERE scan_time > TIMESTAMP'{date}' - INTERVAL'7 days' AND person_email = '{email}'
        )
        SELECT DISTINCT scans.person_email
        FROM rooms_attended, scans
        WHERE scans.person_email != '{email}' AND scans.room_id = rooms_attended.room_id AND (scans.scan_time BETWEEN rooms_attended.scan_time - INTERVAL'1 hour' AND rooms_attended.scan_time + INTERVAL'1 hour') AND (sqrt(power(rooms_attended.x_pos - scans.x_pos,2) + power(rooms_attended.y_pos - scans.y_pos,2)) < 10); 
    """)

     
    contacts = cur.fetchall()

    #query all students that infected student has been in contact with outside of classroom
    cur = _execute_statement(conn, f"""
        SELECT DISTINCT scanned_email
        FROM personal_scans
        WHERE scanner_email = '{email}' AND scan_time > TIMESTAMP'{date}' - INTERVAL'7 days'; 
    """)

    contacts += cur.fetchall()

    cur.close()

    if(len(contacts) == 0):
        return None
    
    return contacts

#get all people and the amount of scans they have
def get_people(conn):

    cur = _execute_statement(conn, 
        f"""SELECT email,name,student_id,
        (
            SELECT COUNT(person_email)
            FROM scans
            WHERE scans.person_email = people.email 
        )
        FROM people 
        """)

    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchall()

    if(len(result) == 0):
        return None
    

    cur.close()

    return result

#get records count
def get_records_count(conn) -> int:

    cur = _execute_statement(conn, f"SELECT COUNT(scan_id) FROM scans")

    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchone()
    
    cur.close()

    return result[0]

#gets number of students in database
def get_students_count(conn) -> int:
    cur = _execute_statement(conn, 
    f"""
        SELECT COUNT(email)
        FROM people;
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")

    result = cur.fetchone()

    return result[0]

#gets number of rooms in database
def get_rooms_count(conn) -> int:
    cur = _execute_statement(conn, 
    f"""
        SELECT COUNT(room_id)
        FROM rooms;
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")

    result = cur.fetchone()

    return result[0]

#gets room id, capacity, building name, the total number of scans that happened in the room,
#count of unique students that have scanned in the room, and # of scans per day for that room 
def get_rooms(conn):

    cur = _execute_statement(conn, 
    f"""
        SELECT *,
        (
            SELECT COUNT(scan_id)
            FROM scans s
            INNER JOIN rooms r
            ON s.room_id = r.room_id
        ),
        (
            SELECT COUNT (person_email)
            FROM (SELECT DISTINCT person_email FROM scans s INNER JOIN rooms r ON s.room_id = r.room_id) AS temp
        )
        
        FROM rooms
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchall()

    if(len(result) == 0):
        return None

    #add scans per day
    for i in range(len(result)):
        List = list(result[i])
        List.append(round(List[4] / 14,1))
        result[i] = tuple(List)
        
    return result

def get_room(room_id:str, conn):

    cur = _execute_statement(conn, 
    f"""
        SELECT *,
        (
            SELECT COUNT(scan_id)
            FROM scans
            WHERE room_id = '{room_id}'
        ),
        (
            SELECT COUNT (person_email)
            FROM (SELECT DISTINCT person_email FROM scans WHERE room_id = '{room_id}') AS temp
        )
        
        FROM rooms
        WHERE room_id = '{room_id}'
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchall()

    
    if(len(result) == 0):
        return None
    
    #add scans per day
    List = list(result[0])
    List.append(round(List[4] / 14,1))

    return tuple(List)
    
#gets number of buildings in database
def get_buildings_count(conn) -> int:
    cur = _execute_statement(conn, 
    f"""
        SELECT COUNT(building_name)
        FROM (SELECT DISTINCT building_name FROM rooms) as temp;
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")

    result = cur.fetchone()

    return result[0]

#gets building name, # of rooms in that building, # of scans that has been made in that building,
# the total number of unique students that scanned in that building, and scans per day 
def get_buildings(conn):

    cur = _execute_statement(conn, 
    f"""
        SELECT DISTINCT building_name,
        (
            SELECT COUNT (room_id)
            FROM rooms AS rooms_2
            WHERE rooms_2.building_name = rooms_1.building_name
        ),
        (
            SELECT COUNT(scan_id)
            FROM scans AS scans_1, rooms AS rooms_3
            WHERE scans_1.room_id = rooms_3.room_id AND rooms_1.building_name = rooms_3.building_name
        ),
        (
            SELECT COUNT(DISTINCT person_email)
            FROM scans as scans_2, rooms AS rooms_4
            WHERE scans_2.room_id = rooms_4.room_id AND rooms_1.building_name = rooms_4.building_name
        )
        
        FROM rooms AS rooms_1
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchall()

    if(len(result) == 0):
        return None

    #add scans per day
    for i in range(len(result)):
        List = list(result[i])
        List.append(round(List[2] / 14,1))
        result[i] = tuple(List)
    
    return result    

def get_building(building_name:str, conn):

    cur = _execute_statement(conn, 
    f"""
        SELECT DISTINCT building_name,
        (
            SELECT COUNT (room_id)
            FROM rooms AS rooms_2
            WHERE rooms_2.building_name = rooms_1.building_name
        ),
        (
            SELECT COUNT(scan_id)
            FROM scans AS scans_1, rooms AS rooms_3
            WHERE scans_1.room_id = rooms_3.room_id AND rooms_1.building_name = rooms_3.building_name
        ),
        (
            SELECT COUNT(DISTINCT person_email)
            FROM scans as scans_2, rooms AS rooms_4
            WHERE scans_2.room_id = rooms_4.room_id AND rooms_1.building_name = rooms_4.building_name
        )
        
        FROM rooms AS rooms_1
        WHERE building_name = '{building_name}'
    """)
    
    if cur is None:
        raise LookupError("Error occured while executing the SQL statement")
    
    result = cur.fetchall()

    if(len(result) == 0):
        return None

    #add scans per day
    List = list(result[0])
    List.append(round(List[2] / 14,1))
    
    return tuple(List)

    