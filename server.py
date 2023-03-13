from fastapi import FastAPI, Form
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


@app.post("/login")
def process_login_page(
    username : str = Form(...), 
    password : str = Form(...)
    ):
    return Response(
        f"Твой логин: {username}, Твой пароль: {password}",
        media_type="text/html",     
    )
