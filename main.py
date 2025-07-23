from typing import Union
import mysql.connector, os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

import modele

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("HOST"),
    database=os.getenv("BDD"),
    user=os.getenv("USER"),
    password=os.getenv("PW")
)

class Item(BaseModel):
    id: int
    name: str
    price: float
    is_offer: Union[bool, None] = None

bouffe = [Item(id=1, name="Patates (2kg)", price=10.0), Item(id=2, name="Chips barbebue (1.5kg)", price=5.0)]

@app.get("/catalogue", name="catalogue")
async def catalogue(request: Request):
    return templates.TemplateResponse(
        request=request, name="catalogue.html", context={"items": bouffe}
    )

@app.get("/item/{id}", name="view_item")
async def view_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"item": bouffe[int(id) - 1]}
    )

@app.get("/json/item/{id}", name="view_item")
def view_item(request: Request, id: str):
    return {"item": bouffe[int(id) - 1]}

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })


@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    cp: str = Form(default=None),
    selected_city: str = Form(default=None)
):
    error = None
    communes = []
    weather = None

    if selected_city :
        weather = modele.get_weather_from_dbb(selected_city, mydb)
        if not weather:
            error = "Erreur météo"
        return templates.TemplateResponse("index.html", {
            "request": request,
            "weather": weather,
            "city": selected_city,
            "error": error
        })

    elif cp:
        communes = modele.getNomCommuneCodeCommuneFromCodePostal(cp, mydb)
        if not communes:
            error = "Aucune commune trouvée pour ce code postal."
        return templates.TemplateResponse("index.html", {
            "request": request,
            "communes": communes,
            "cp": cp,
            "error": error
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": "Code postal requis."
    })