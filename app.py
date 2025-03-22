from typing import Self
from fastapi import FastAPI, UploadFile, File
from datetime import datetime
import hashlib
import psycopg2

class DatabaseConnection:
	def __init__(self: Self) -> None:
		self.conn_params = {
			"dbname": "filestore",
			"user": "admin",
			"password": "secretpassword",
			"host": "db",
			"port": "5432"
		}
	
	def store_file(self: Self, file_data: bytes, file_hash: str) -> None:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"INSERT INTO files (file_hash, file_data, file_size) VALUES (%s, %s, %s)",
					(file_hash, file_data, len(file_data))
				)

app = FastAPI()
db = DatabaseConnection()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
	# Read the file content
	content = await file.read()
	
	# Generate SHA-256 hash of the file
	file_hash = hashlib.sha256(content).hexdigest()
	
	# Store in database
	db.store_file(content, file_hash)
	
	return {"hash": file_hash} 