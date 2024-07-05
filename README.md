# Web Service based on FastAPI

## How to run 

### Clone this repo
```
git clone https://github.com/zakh-d/python-fs-internship-backend.git
```

### Set env variables
Create .env file based on .env.example file

### Run using docker compose
This requires you to have [Docker](https://www.docker.com) installed on your PC.
```
docker compose up -d
```

### Run tests
```
docker compose exec api pytest
```