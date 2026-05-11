from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI)

db = client["Hospital_Management_HMS"]

users = db["users"]
appointments = db["appointments"]
payments = db["payments"]
medical_records = db["medical_records"]
