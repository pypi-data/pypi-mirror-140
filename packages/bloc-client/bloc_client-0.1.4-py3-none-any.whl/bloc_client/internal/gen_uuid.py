from hashlib import new
import uuid

def new_uuid() -> str:
    return str(uuid.uuid1())
