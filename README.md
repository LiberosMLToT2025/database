# database

Example usage:

Upload file to database:
`curl -X POST -F "file=@test.txt" http://localhost:8000/upload/`
Returns: {"id": 1, "hash": "123...abc"}

Register a transaction for that file:
`curl -X POST http://localhost:8000/register_transaction/1/TX123456`
Returns: {"success": true}

Download stored file by database record id:
`curl http://localhost:8000/download/1 --output downloaded_file`

Download stored file by blockchain transaction id:
`curl http://localhost:8000/download_by_transaction/TX123456 --output downloaded_file`

Validate file integrity:
`curl "http://localhost:8000/validate/1/123...abc"`
Returns: {"is_valid": true}

Clear database:
`curl -X POST http://localhost:8000/clear`
Returns: {"files_deleted": 42}