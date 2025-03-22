from typing import Self
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
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
	
	def store_file(self: Self, file_data: bytes, file_hash: str) -> int:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"INSERT INTO files (file_hash, file_data, file_size) VALUES (%s, %s, %s) RETURNING id",
					(file_hash, file_data, len(file_data))
				)
				# Get the inserted row's id
				file_id = cur.fetchone()[0]
				return file_id
	
	def get_file(self: Self, file_id: int) -> tuple[bytes, str] | None:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"SELECT file_data, file_hash FROM files WHERE id = %s",
					(file_id,)
				)
				result = cur.fetchone()
				if result is None:
					return None
				return result[0], result[1]  # returns (file_data, file_hash)
	
	def clear_database(self: Self) -> int:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute("DELETE FROM files")
				# Get number of rows deleted
				deleted_count = cur.rowcount
				# Reset the auto-increment counter
				cur.execute("ALTER SEQUENCE files_id_seq RESTART WITH 1")
				return deleted_count

app = FastAPI()
db = DatabaseConnection()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str | int]:
	# Read the file content
	content = await file.read()
	
	# Generate SHA-256 hash of the file
	file_hash = hashlib.sha256(content).hexdigest()
	
	# Store in database and get the file id
	file_id = db.store_file(content, file_hash)
	
	return {
		"id": file_id,
		"hash": file_hash
	}

@app.get("/download/{file_id}")
async def download_file(file_id: int) -> Response:
	result = db.get_file(file_id)
	if result is None:
		raise HTTPException(status_code=404, detail="File not found")
	
	file_data, _ = result
	# Return the file as a binary response
	return Response(
		content=file_data,
		media_type="application/octet-stream",
		headers={
			"Content-Disposition": f"attachment; filename=file_{file_id}"
		}
	)

@app.get("/validate/{file_id}/{file_hash}")
async def validate_file(file_id: int, file_hash: str) -> dict[str, bool]:
	result = db.get_file(file_id)
	if result is None:
		raise HTTPException(status_code=404, detail="File not found")
	
	file_data, stored_hash = result
	# Calculate hash of stored file
	calculated_hash = hashlib.sha256(file_data).hexdigest()
	
	return {
		"is_valid": calculated_hash == file_hash and stored_hash == file_hash
	}

@app.post("/clear")
async def clear_database() -> dict[str, int]:
	deleted_count = db.clear_database()
	return {
		"files_deleted": deleted_count
	} 