from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }
    
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    homeworld_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    homeworld = db.relationship('Planet')

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "homeworld": self.homeworld.serialize() if self.homeworld else None,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.username,
            "email": self.email,
        }
    
class FavoritePlanet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet = db.relationship('Planet')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def serialize(self):
        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "planet_name": self.planet.name,
        }
    
class FavoriteCharacter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    character = db.relationship('Character')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def serialize(self):
        return {
            "id": self.id,
            "character_id": self.character_id,
            "character_name": self.character.name,
        }
