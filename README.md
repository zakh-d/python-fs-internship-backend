# Web Service based on FastAPI

## How to run 

### Clone this repo
```
git clone https://github.com/zakh-d/python-fs-internship-backend.git
```

### Set up venv and download requirements
**Create new virtual environment**
```
python3 -m venv venv
```

**Activate your virtual environment**

for linux/macos:
```
source venv/bin/activate
```
for windows:
```
./venv/Scripts/activate
```

**Download requirements**

```
pip install -r requirements.txt
```

### Run webserver
You can run FastAPI applicatio using FastAPI CLI or using ASGI webserver 

**FastAPI CLI**

for development (auto-reload enabled by default)
```
fastapi dev app/main.py
```

for production
```
fastapi run app/main.py
```

**ASGI webserver (uvicorn):**
```
uvicorn --reload app.main:app
```

### Run tests
```
python -m pytest
```