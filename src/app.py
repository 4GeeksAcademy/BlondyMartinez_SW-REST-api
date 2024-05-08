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


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
