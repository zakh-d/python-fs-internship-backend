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
### Apply migrations
Apply migrations to the db inside docker container. Check [here](#applying-existing-alembic-migrations) how to do this.
## Database migrations

### Applying existing alembic migrations
To apply existing alembic migration to postgres inside docker container run following command
```
docker compose exec api alembic upgrade head
```
this would apply all existing migrations to the db.

### Creating new alembic migrations
To create new alembic migration run following command
```
 docker compose exec api alembic revision --autogenerate -m 'migration description'
```
this would automatically check models, that were inheritted from ```Base``` class in ```app.db.models``` module, whether there were any changes, if so I would generate migrations files inside ```app/db/migrations``` folder. You **MUST** check created file

## Testing
```
docker compose exec api pytest
```