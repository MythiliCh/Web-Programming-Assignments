from mongita import MongitaClientDisk
import uuid

client = MongitaClientDisk()
session_db = client.session_db

def create_session(user):
    session_id = str(uuid.uuid4())
    session_collection = session_db.session_collection
    session_data = {"session_id": session_id, "user": user}
    session_collection.insert_one(session_data)
    return session_id

def delete_session(session_id):
    session_collection = session_db.session_collection
    session_collection.delete_one({"session_id": session_id})

def get_session(session_id):
    session_collection = session_db.session_collection
    return session_collection.find_one({"session_id": session_id})
