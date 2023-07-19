from data_store import Base, engine
from interface import BotInterface
from config import comunity_token, acces_token
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()