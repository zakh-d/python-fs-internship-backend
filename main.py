from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def get_root_status_checks():
    return {
        'status_code': 200,
        'details': 'ok',
        'result': 'working'
    }
