import requests, os
from dotenv import load_dotenv

def getNomCommuneCodeCommuneFromCodePostal(codePostal, db):
    curseur = db.cursor()
    sql = f"select Nom_de_la_commune, Code_commune_INSEE from datascommunes where Code_postal = {codePostal}"
    curseur.execute(sql)
    res = curseur.fetchall()
    curseur.nextset()
    curseur.close()
    if len(res) > 0 :
        result = []
        for loop in res:
            result.append({'nomCommune': loop[0], 'codeCommune': loop[1]})
        return result
    return None

def getNomCommuneFromCodeCommune(codeCommune, db):
    curseur = db.cursor()
    sql = f"select Nom_de_la_commune from datascommunes where Code_commune_INSEE = {codeCommune}"
    curseur.execute(sql)
    res = curseur.fetchone()
    curseur.close()
    if len(res) > 0:
        return res[0]
    return None

def getCodePostalFromCodeCommune(codeCommune, db):
    curseur = db.cursor()
    sql = f"select Code_postal from datascommunes where Code_commune_INSEE = {codeCommune}"
    curseur.execute(sql)
    res = curseur.fetchone()
    curseur.close()
    print(res)
    if len(res) > 0:
        return res[0]
    return None

def get_weather(city):
    load_dotenv()
    api_key = os.getenv("API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},fr&appid={api_key}&units=metric&lang=fr"
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            print(data)
            return {
                "description": data["weather"][0]["description"],
                "temp": data["main"]["temp"],
                "ressentie": data["main"]["feels_like"],
                "humidite": data["main"]["humidity"],
                "vent": data["wind"]["speed"]
            }
    except Exception as e:
        print("Erreur API météo :", e)
    return None

def get_weather_from_dbb(city, db):
    curseur = db.cursor()
    sql = """
          SELECT description, temp, ressentie, humidite, vent, date_insertion, heure_insertion, Nom_de_la_commune
          FROM datascommunes
          WHERE Code_commune_INSEE = %s
              AND CONCAT(date_insertion, ' ', heure_insertion) >= NOW() - INTERVAL 1 HOUR
          """
    curseur.execute(sql, (city,))
    res = curseur.fetchone()

    if res:
        curseur.close()
        return {
            "description": res[0],
            "temp": res[1],
            "ressentie": res[2],
            "humidite": res[3],
            "vent": res[4],
            "nom": res[7]
        }

    city2 = getCodePostalFromCodeCommune(city, db)
    weather_data = get_weather(city2)
    if weather_data:
        sql_update = """
                     UPDATE datascommunes
                     SET description     = %s, \
                         temp            = %s, \
                         ressentie       = %s, \
                         humidite        = %s, \
                         vent            = %s, \
                         date_insertion  = CURDATE(),
                         heure_insertion = CURTIME()
                     WHERE Code_commune_INSEE = %s \
                     """
        curseur.execute(sql_update, (
            weather_data["description"],
            weather_data["temp"],
            weather_data["ressentie"],
            weather_data["humidite"],
            weather_data["vent"],
            city
        ))
        db.commit()
        curseur.close()
        nom = getNomCommuneFromCodeCommune(city, db)
        if nom is not None:
            weather_data["nom"] = nom
        return weather_data

    curseur.close()
    return None