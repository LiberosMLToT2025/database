# File Storage API

A FastAPI-based service for storing files with transaction ID and hash verification capabilities.

## API Endpoints

### Upload a File
```bash
curl -X POST -F "file=@path/to/input/file.txt" http://localhost:8000/upload/
```
Response:
```json
{
    "id": 1
}
```

### Register a Transaction
First calculate the SHA-256 hash of your file, then register the transaction:
```bash
# Calculate hash (example using command line)
FILE_HASH=$(sha256sum path/to/input/file.txt | cut -d' ' -f1)

# Register transaction
curl -X POST http://localhost:8000/register_transaction/1/TX123456/$FILE_HASH
```
Response:
```json
{
    "success": true
}
```

### Download a File
By file ID:
```bash
curl http://localhost:8000/download/1 --output path/to/output/file.txt
```

By transaction ID:
```bash
curl http://localhost:8000/download_by_transaction/TX123456 --output path/to/output/file.txt
```

### Validate a File
```bash
curl http://localhost:8000/validate/1/$FILE_HASH
```
Response:
```json
{
    "is_valid": true
}
```

### Clear Database
```bash
curl -X POST http://localhost:8000/clear
```
Response:
```json
{
    "files_deleted": 42
}
```