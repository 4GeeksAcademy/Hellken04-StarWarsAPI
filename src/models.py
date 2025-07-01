import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__='user'
    ID: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str]=mapped_column(String(100), nullable=False)
    member_since: Mapped[datetime.date]=mapped_column(Date(),nullable=False)
    firstname: Mapped[str]=mapped_column(String(100), nullable=False)
    lastname: Mapped[str]=mapped_column(String(100), nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean,nullable=False, default=True)
    favorites: Mapped[list['FavoriteCharacters']]=relationship(back_populates='user')
    favorite_planets: Mapped[list['FavoritePlanets']]=relationship(back_populates='user')
    
    def serialize(self):
        return {
            "id": self.ID,
            "email": self.email,
            "member_since": self.member_since,
            "firstname":self.firstname,
            "lastname":self.lastname,
            "is_active":self.is_active
        }
    
    def __str__(self):
        return f'User {self.email}'

class Characters(db.Model):
    __tablename__='characters'
    ID: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]= mapped_column(String(120), nullable=False)
    height: Mapped[int]= mapped_column(Integer)
    weight: Mapped[int]= mapped_column(Integer)
    favorite_by: Mapped[list['FavoriteCharacters']]=relationship(back_populates='character')

    def serialize (self):
        return{
            "id":self.ID,
            "name":self.name,
            "height":self.height,
            "weight":self.weight
        }
    
    def __str__(self):
        return f'Character {self.name}'

class Planets (db.Model):
    __tablename__='planets'
    ID: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    population: Mapped[int]=mapped_column(Integer)
    favorite_by:Mapped[list['FavoritePlanets']]=relationship(back_populates='planet')

    def serialize(self):
        return{
            "id":self.ID,
            "name":self.name,
            "population":self.population
        }
    
    def __str__(self):
        return f'Planet {self.name}'

class FavoriteCharacters(db.Model):
    __tablename__='favorite_characters'
    ID: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped [int] = mapped_column(ForeignKey('user.ID'))
    user: Mapped['User']= relationship(back_populates='favorites')
    character_id: Mapped [int] = mapped_column(ForeignKey('characters.ID'))
    character: Mapped['Characters']= relationship(back_populates='favorite_by')

    def __str__(self):
        return f'{self.user} likes {self.character}'
    
    

class FavoritePlanets (db.Model):
    __tablename__='favorite_planets'
    ID : Mapped[int]= mapped_column(primary_key=True)
    user_id: Mapped [int]=mapped_column(ForeignKey('user.ID'))
    user: Mapped['User']=relationship(back_populates='favorite_planets')
    planet_id:Mapped [int]= mapped_column(ForeignKey('planets.ID'))
    planet: Mapped['Planets']=relationship(back_populates='favorite_by')

    def __str__(self):
        return f'{self.user} likes {self.planet}' 
