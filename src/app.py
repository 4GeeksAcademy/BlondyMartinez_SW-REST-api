"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, FavoriteCharacter, FavoritePlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# users below
@app.route('/users', methods=['GET'])
def get_users():
    all_users = list(map(lambda user: user.serialize(), User.query.all()))
    return jsonify(all_users), 200

@app.route('/users', methods=["POST"]) 
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password: return jsonify({'error': 'missing field'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user: return jsonify({'error': 'email is already in use'}), 400

    new_user = User(username=username, email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email
    }), 201

@app.route("/users/<int:position>", methods=["GET"])
def get_user(position):
    user = User.query.get(position)
    return jsonify(user.serialize()), 200

@app.route("/users/<int:position>", methods=["DELETE"])
def delete_user(position):
    user = User.query.get(position)

    if not user: return jsonify({'error': 'not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'deleted successfully'}), 200

@app.route("/users/<int:position>", methods=["PUT"])
def update_user(position):
    user = User.query.get(position)

    if not user: return jsonify({'error': 'not found'}), 404

    data = request.json
    new_username = data.get('username')
    new_email = data.get('email')
    new_password = data.get('password')

    if new_username: user.username = new_username
    if new_email: user.email = new_email
    if new_password: user.password = new_password

    db.session.commit()

    return jsonify(user.serialize()), 200

# characters below
@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = list(map(lambda character: character.serialize(), Character.query.all()))
    return jsonify(all_characters), 200

@app.route('/characters', methods=["POST"]) 
def create_character():
    data = request.json
    name = data.get('name')
    homeworld_id = data.get('homeworld')

    if not name or not homeworld_id: return jsonify({'error': 'missing field'}), 400
    
    homeworld = Planet.query.get(homeworld_id)

    if not homeworld: return jsonify({'error': 'invalid homeworld id'}), 400

    existing_character = Character.query.filter_by(name=name).first()
    if existing_character: return jsonify({'error': 'character is already on the database'}), 400

    new_character = Character(name=name, homeworld_id=homeworld_id)

    db.session.add(new_character)
    db.session.commit()

    return jsonify({
        'id': new_character.id,
        'name': new_character.name,
        'homeworld_id': new_character.homeworld_id,
        'homeworld': homeworld.name,
    }), 201

@app.route("/characters/<int:position>", methods=["GET"])
def get_character(position):
    character = Character.query.get(position)
    if character: return jsonify(character.serialize()), 200
    else: return jsonify({'error': 'not found'}), 404

@app.route("/characters/<int:position>", methods=["DELETE"])
def delete_character(position):
    character = Character.query.get(position)

    if not character: return jsonify({'error': 'not found'}), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({'message': 'deleted successfully'}), 200

@app.route("/characters/<int:position>", methods=["PUT"])
def update_character(position):
    character = Character.query.get(position)

    if not character: return jsonify({'error': 'not found'}), 404

    data = request.json
    new_name = data.get('name')
    new_homeworld_id = data.get('homeworld')

    existing_character = Character.query.filter_by(name=new_name).first()
    if existing_character: return jsonify({'error': 'character with that name is already on the database'}), 400

    homeworld = Planet.query.get(new_homeworld_id)
    if new_homeworld_id and not homeworld: return jsonify({'error': 'invalid homeworld id'}), 400

    if new_name: character.name = new_name
    if new_homeworld_id: character.homeworld_id = new_homeworld_id

    db.session.commit()

    return jsonify(character.serialize()), 200

# planets below
@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = list(map(lambda planet: planet.serialize(), Planet.query.all()))
    return jsonify(all_planets), 200

@app.route('/planets', methods=["POST"]) 
def create_planet():
    data = request.json
    name = data.get('name')

    if not name: return jsonify({'error': 'missing field'}), 400

    existing_planet = Planet.query.filter_by(name=name).first()
    if existing_planet: return jsonify({'error': 'planet already exists in the database'}), 400

    new_planet = Planet(name=name)

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({
        'id': new_planet.id,
        'name': new_planet.name,
    }), 201

@app.route("/planets/<int:position>", methods=["GET"])
def get_planet(position):
    planet = Planet.query.get(position)
    return jsonify(planet.serialize()), 200

@app.route("/planets/<int:position>", methods=["DELETE"])
def delete_planet(position):
    planet = Planet.query.get(position)

    if not planet: return jsonify({'error': 'not found'}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({'message': 'deleted successfully'}), 200

@app.route("/planets/<int:position>", methods=["PUT"])
def update_planet(position):
    planet = Planet.query.get(position)

    if not planet: return jsonify({'error': 'not found'}), 404

    data = request.json
    new_name = data.get('name')

    if new_name: planet.name = new_name

    db.session.commit()

    return jsonify(planet.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
