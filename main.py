from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import redis

app = FastAPI()

# Configure Redis client
# Ensure you configure these settings according to your Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class Announcement(BaseModel):
    message: str
    send_time: str  # ISO format datetime string

def generate_idempotency_key() -> str:
    return str(uuid.uuid4())

def check_for_duplicates(idempotency_key: str) -> bool:
    # Checks if the announcement has already been processed using Redis
    return redis_client.exists(idempotency_key)

def replicate_across_servers(idempotency_key: str, announcement_data: str):
    # Use Redis to replicate announcement data across servers
    # The data is stored with the idempotency key as the key
    redis_client.set(idempotency_key, announcement_data)

@app.post("/announcements/")
async def create_announcement(announcement: Announcement):
    idempotency_key = generate_idempotency_key()
    if check_for_duplicates(idempotency_key):
        return {"status": "Duplicate", "detail": "Announcement already sent"}

    announcement_data = {
        "message": announcement.message,
        "send_time": announcement.send_time
    }

    # Serialize announcement data for storage in Redis
    # In a real application, consider using JSON or another serialization format
    announcement_data_serialized = str(announcement_data)

    replicate_across_servers(idempotency_key, announcement_data_serialized)

    # Placeholder for sending the announcement to WhatsApp
    send_announcement_to_whatsapp(announcement.message)

    return {"status": "Success", "detail": "Announcement sent"}

@app.get("/announcements/{idempotency_key}")
async def get_announcement(idempotency_key: str):
    announcement_data_serialized = redis_client.get(idempotency_key)
    if not announcement_data_serialized:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Deserialize announcement data
    # For demonstration purposes, this is a simple conversion back from a string
    # A real application would use a proper serialization/deserialization approach
    announcement_data = eval(announcement_data_serialized)
    
    return announcement_data

def send_announcement_to_whatsapp(message: str):
    # Simulated function to send announcements via WhatsApp
    print(f"Sending announcement to WhatsApp: {message}")
