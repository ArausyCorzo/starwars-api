"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code 

def swapi_to_localhost(URL_swapi):
    return URL_swapi.replace("https://www.swapi.tech/api/", "https://3000-pink-vulture-dflm8tzj.ws-us25.gitpod.io/")

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#GET all planets
@app.route('/<string:nature>', methods=['GET'])
def handle_get_natures(nature):
    #request satrwars' api
    if nature == "planets" or nature == "people" or nature == "vehicles":
        response = requests.get(f"https://www.swapi.tech/api/{nature}?page=1&limit=1000")
        response = response.json()
        results = response['results']

        for result in results:
            result.update(url = swapi_to_localhost(result["url"]))
        return jsonify(results), 200

@app.route('/favorites/<string:nature>', methods=['POST'])
def handle_favorite(nature):
    uid = request.json["uid"]
    name = request.json["name"]
    user_id = request.json["user_id"]
    new_favorite = Favorite(
        user_id = user_id,
        name = name, 
        url = f"https://www.swapi.tech/api/{nature}/{uid}"
    )

    db.session.add(new_favorite)
    try:
        db.session.commit()
        return jsonify(new_favorite.serialize()), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(error.args), 500

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
