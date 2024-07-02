from fastapi import FastAPI

app = FastAPI()


@app.get('/', description='Health check')
def get_root_status_checks():
    return {
        'status_code': 200,
        'details': 'ok',
        'result': 'working'
    }
