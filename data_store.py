import vk_api
import sqlalchemy
from sqlalchemy.orm import declarative_base, relationship, backref, sessionmaker
from sqlalchemy import Column, String, Integer, Double, DateTime, ForeignKey, Boolean
from config import db_url_object, comunity_token, acces_token
from core import VkTools
from sqlalchemy.exc import IntegrityError, InvalidRequestError

vk = vk_api.VkApi(token=comunity_token)

Base = declarative_base()

engine = sqlalchemy.create_engine(db_url_object)
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True)

class Profiles(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True)
    name = Column(String(255))
    id_user = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

# class FavoriteList(Base):
#     __tablename__ = 'favoriteList'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vk_id = Column(Integer, unique=True)
#     id_favorite_user = Column(Integer, ForeignKey('profiles.id'))
#
# class BlackList(Base):
#     __tablename__ = 'blackList'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     vk_id = Column(Integer, unique=True)
#     id_user = Column(Integer, ForeignKey('users.id'))


""" 
Functions of database
"""

def add_bot_user(vk_id):
    try:
        new_user = Users(
            vk_id=vk_id
        )
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False

def check_bot_user(vk_id):
    return session.query(Users).filter_by(vk_id=vk_id).first()

def get_id_db_user(vk_id):
    result = session.query(Users).filter_by(vk_id=vk_id).first()
    return result.id

def add_profile(vk_id, name, id_user):
    try:
        new_profile = Profiles(
            vk_id=vk_id,
            name=name,
            id_user=id_user
        )
        session.add(new_profile)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False

def check_user_in_profiles(vk_id):
    result = session.query(Profiles).filter_by(vk_id=vk_id).first()
    return result

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    bot = VkTools(acces_token)
    params = bot.get_profile_info(554973226)
    print(add_bot_user(params['id']))
    print(get_id_db_user(params['id']))
    print(add_profile(params["id"], params["name"], get_id_db_user(params["id"])))
    print('/n')
    print(check_user_in_profiles(params["id"]))
