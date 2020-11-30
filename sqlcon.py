import mysql.connector

def connect():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="bookmart"
        )
    return db