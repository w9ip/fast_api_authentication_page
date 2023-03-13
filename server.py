from fastapi import FastAPI
from fastapi.responses import Response


app = FastAPI() 


@app.get("/")
def index_page():
    """A main site's page"""
    
    with open('templates/login.html', 'r') as f:
        html_login_page = f.read()
        
    return Response(
        html_login_page,
        media_type="text/html",
    )

