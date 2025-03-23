from typing import Self
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
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
	
	def get_file_by_transaction(self: Self, transaction_id: str) -> tuple[bytes, str, int] | None:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"SELECT file_data, file_hash, id FROM files WHERE transaction_id = %s",
					(transaction_id,)
				)
				result = cur.fetchone()
				if result is None:
					return None
				return result[0], result[1], result[2]  # returns (file_data, file_hash, file_id)
	
	def clear_database(self: Self) -> int:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute("DELETE FROM files")
				# Get number of rows deleted
				deleted_count = cur.rowcount
				# Reset the auto-increment counter
				cur.execute("ALTER SEQUENCE files_id_seq RESTART WITH 1")
				return deleted_count
	
	def register_transaction(self: Self, file_id: int, transaction_id: str, file_hash: str) -> bool:
		with psycopg2.connect(**self.conn_params) as conn:
			with conn.cursor() as cur:
				cur.execute(
					"UPDATE files SET transaction_id = %s, file_hash = %s WHERE id = %s AND transaction_id IS NULL RETURNING id",
					(transaction_id, file_hash, file_id)
				)
				# Return True if a row was updated, False if no row was found or already had transaction_id
				return cur.fetchone() is not None

app = FastAPI()

# Dodanie middleware CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

db = DatabaseConnection()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> dict[str, int]:
	# Read the file content
	content = await file.read()
	
	# Store in database and get the file id
	file_id = db.store_file(content, "")	# empty hash initially
	
	return {
		"id": file_id
	}

@app.post("/register_transaction/{file_id}/{transaction_id}/{file_hash}")
async def register_transaction(file_id: int, transaction_id: str, file_hash: str) -> dict[str, bool]:
	# Get file data to verify hash
	result = db.get_file(file_id)
	if result is None:
		raise HTTPException(status_code=404, detail="File not found")
	
	file_data, _ = result
	# Verify the provided hash matches the file content
	calculated_hash = hashlib.sha256(file_data).hexdigest()
	if calculated_hash != file_hash:
		raise HTTPException(status_code=400, detail="Invalid file hash")
	
	# Update file hash and register transaction
	success = db.register_transaction(file_id, transaction_id, file_hash)
	if not success:
		raise HTTPException(
			status_code=400,
			detail="File not found or transaction already registered"
		)
	
	return {"success": True}

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

@app.get("/download_by_transaction/{transaction_id}")
async def download_file_by_transaction(transaction_id: str) -> Response:
	result = db.get_file_by_transaction(transaction_id)
	if result is None:
		raise HTTPException(status_code=404, detail="File not found for this transaction ID")
	
	file_data, _, file_id = result
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