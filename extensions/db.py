import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hms"
)

cursor = db.cursor(dictionary=True)
