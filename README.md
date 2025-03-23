# database

Example usage:

Upload file to database:\
`curl -X POST -F "file=@path/to/input/file.txt" http://localhost:8000/upload/`\
Example expected return: `{"id": 1, "hash": "123...abc"}`

Register a transaction for that file:\
`curl -X POST http://localhost:8000/register_transaction/1/TX123456`\
Example expected return: `{"success": true}`

Download stored file by database record id:\
`curl http://localhost:8000/download/1 --output path/to/output/file.txt`\

Download stored file by blockchain transaction id:\
`curl http://localhost:8000/download_by_transaction/TX123456 --output path/to/output/file.txt`\

Validate file integrity:\
`curl "http://localhost:8000/validate/1/123...abc"`\
Example expected return: `{"is_valid": true}`

Clear database:\
`curl -X POST http://localhost:8000/clear`\
Example expected return: `{"files_deleted": 42}`