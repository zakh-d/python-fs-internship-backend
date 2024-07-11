FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY alembic.ini /code/alembic.ini
COPY ./app /code/app

CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "80"]