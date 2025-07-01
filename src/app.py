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
from models import db, User, Characters, Planets, FavoriteCharacters, FavoritePlanets
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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def list_all_users():
    users=User.query.all()
    users_serialized=[]
    for user in users:
        users_serialized.append( user.serialize())
    print (users_serialized)
    return jsonify({'msg':'Usuarios listados correctamente', 'users': users_serialized})

@app.route ('/users/<int:user_id>', methods=['GET'])
def list_user (user_id):
    user=User.query.get(user_id)
    if user is None:
        return jsonify({'msg':'El usuario no existe'}), 404
    print (user.serialize())
    return jsonify({'msg':'Usuario Listado con exito','user':user.serialize()})

@app.route('/user', methods=['POST'])
def create_user():
    body= request.get_json(silent=True)
    if body is None:
        return jsonify({'msg':'Debe enviar información'}), 400
    if 'email' not in body:
        return jsonify({'msg':'Debe ingresar el e-mail'}), 400
    if 'password' not in body:
        return jsonify({'msg':'Debe ingresar el password'}), 400
    if 'member_since' not in body:
        return jsonify({'msg':'Debe ingresar una fecha de creación'}), 400
    if 'firstname' not in body:
        return jsonify({'msg':'Debe ingresar el nombre'}), 400
    if 'lastname' not in body:
        return jsonify({'msg':'Debe ingresar el apellido'}), 400
    
    new_user = User()
    new_user.email=body['email']
    new_user.password=body['password']
    new_user.member_since=body['member_since']
    new_user.firstname=body['firstname']
    new_user.lastname=body['lastname']
    db.session.add(new_user)
    db.session.commit()
    return jsonify ({'msg':'registro exitoso','user': new_user.serialize()})

@app.route ('/users/<int:user_id>/favorites_characters', methods=['GET'])
def get_user_favorites (user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({'msg':f'El usuario con id {user_id} no existe'}), 404
    print (user.favorites)
    favorites_characters_serialized=[]
    for favorite in user.favorites:
        print(favorite.character.serialize())
        favorites_characters_serialized.append(favorite.character.serialize())

    return jsonify ({'msg':'Favoritos listados con exito', 'favorite_characters': favorites_characters_serialized}), 200
    
@app.route('/people', methods=['GET'])
def list_all_characters():
    people=Characters.query.all()
    people_seralized=[]
    for character in people:
        people_seralized.append(character.serialize())
    
    return ({'msg':'Personajes listados con exito','Characters':people_seralized}), 200
    
@app.route ('/people/<int:character_id>', methods=['GET'])
def list_character(character_id):
    character = Characters.query.get(character_id)
    if character is None:
        return jsonify ({'msg': f'El persionaje {character_id} no existe'}), 404
    return jsonify({'msg': 'Personaje Listado correctamente', 'Character': character.serialize()}), 200

@app.route('/planets', methods=['GET'])
def list_all_planets():
    planets=Planets.query.all()
    planets_serialized=[]
    for planet in planets:
        planets_serialized.append( planet.serialize())
    print (planets_serialized)
    return jsonify({'msg':'Planetas listados correctamente', 'Planets': planets_serialized})

@app.route ('/planets/<int:planet_id>', methods=['GET'])
def list_planet (planet_id):
    planet=Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg':'El planeta no existe'}), 404
    print (planet.serialize())
    return jsonify({'msg':'Planeta Listado con exito','Planet':planet.serialize()})

@app.route ('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorite_characters (user_id): 
    user=User.query.get(user_id)
    if user is None:
        return jsonify({'msg':f'El Usuario con id {user_id} no existe'}), 404
    favorite_characters_serialized=[]
    favorite_planets_serialized=[]
    
    for favorite_character_aux in user.favorites:
        print (favorite_character_aux.character.serialize())
        favorite_characters_serialized.append(favorite_character_aux.character.serialize())
     
    for favorite_planet_aux in user.favorite_planets:
        favorite_planets_serialized.append(favorite_planet_aux.planet.serialize())
  
    return (jsonify({'msg':'Favoritos listados con exito', 
                     'Favorite_Characters': favorite_characters_serialized,
                     'Favorite_Planets': favorite_planets_serialized}))

@app.route ('/favorite/<int:user_id>/character/<int:character_id>', methods=['POST'])
def create_favorite_character(user_id,character_id):
    
    user=User.query.get(user_id)
    if user is None:
        return jsonify({'msg':f'El usuario con id {user_id} no existe'})
    
    character=Characters.query.get(character_id)
    if character is None:
        return jsonify({'msg':f'El personaje con id {character_id} no existe'})
    
    favorite_exist = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite_exist is not None:
        return jsonify({'msg':f'El personaje con id {character_id} ya es favorito del usuario {user_id}'})

    favorite = FavoriteCharacters()
    favorite.user_id=user_id
    favorite.character_id=character_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg':'Personaje favorito creado con Exito', 'personaje': character.serialize()})

@app.route ('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(user_id,planet_id):
    user=User.query.get(user_id)
    if user is None:
        return jsonify({'msg':f'El usuario con id {user_id} no existe'})
    planet =Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg':f'El Planeta con Id {planet_id} no existe'})
    
    favorite_exist = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_exist is not None:
        return jsonify({'msg':f'El planeta con id {planet_id} ya es favorito del usuario {user_id}'})

    favorite = FavoritePlanets()
    favorite.user_id=user_id
    favorite.planet_id=planet_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'msg':'Planeta favorito creado con Exito', 'planeta': planet.serialize()})
    
@app.route ('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet (user_id, planet_id):

    favorite_to_delete = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_to_delete is None:
        return jsonify({'msg':f'El favorito con id {planet_id} del usuario  {user_id} no existe'})

    db.session.delete(favorite_to_delete)
    db.session.commit()
    return jsonify({'msg': 'Planeta Favorito eliminado con exito'})

@app.route ('/favorite/<int:user_id>/characters/<int:character_id>', methods=['DELETE'])
def delete_favorite_character (user_id, character_id):
   
    favorite_to_delete = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite_to_delete is None:
        return jsonify({'msg':f'El favorito con id {character_id} del usuario  {user_id} no existe'})

    db.session.delete(favorite_to_delete)
    db.session.commit()
    return jsonify({'msg': 'Personaje Favorito eliminado con exito'})
        
    
    

    


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
