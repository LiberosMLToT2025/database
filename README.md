# database

curl -X POST -F "file=@test.txt" http://localhost:8000/upload/
# Returns: {"id": 1, "hash": "123...abc"}

curl http://localhost:8000/download/1 --output downloaded_file

curl "http://localhost:8000/validate/1/123...abc"
# Returns: {"is_valid": true}

curl -X POST http://localhost:8000/clear
# Returns: {"files_deleted": 42}