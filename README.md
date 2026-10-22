### instructions
```angular2html
uv init
uv add fastapi neo4j uvicorn pydantic-settings
uv add --dev pytest pytest-asyncio httpx ruff
ruff - python linter and formatter
ruff check (linting), ruff format (formatting), ruff check --fix
```

pydantic is data validation and parsing library for Python
httpx - http client for Python, provides sync and async apis and supports http/1.1 & http/2

## neo4j docker shell
```
docker ps
docker exec -it <<neo4j id>> bash


cypher-shell -u neo4j -p your_password
```

even easier don't exec into the container
```
  docker exec -it neo4j \
  cypher-shell -u neo4j -p your_password \
  "MATCH (n) RETURN n LIMIT 25"
  ```

## curl 
Create user
```
curl -X POST http://localhost:8077/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jdoe",
    "password": "hunter2",
    "email": "jdoe@example.com",
    "gender": 1,
    "num_of_reminders": 0
  }'
```

# JWT
## Create  a secret key
```
python -c "import secrets; print(secrets.token_urlsafe(48))"
```