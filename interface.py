# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime
from config import comunity_token, acces_token
from data_store import add_bot_user, add_profile, check_bot_user, check_user_in_profiles, get_id_db_user
from core import VkTools

class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.vkapi = VkTools(acces_token)
        self.params = None
        self.users = []
        self.offset = 0
        self.counter = 30

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def greeting(self, event):
        self.params = self.vkapi.get_profile_info(event.user_id)
        self.message_send(event.user_id, f'Привет, {self.params["name"]}')
        self.message_send(event.user_id, "Я бот, который умеет искать пару, подходящую под условия, "
                                         "на основании твоей информации из VK: возраст, пол, город и "
                                         "семейное положение.")
        self.message_send(event.user_id, "Давай начнем!")
        self.message_send(event.user_id, "Напиши 'Поиск' для осуществление поиска пары!")

    def input_city(self, event, longpoll):
        self.message_send(event.user_id, "У вас не указан город. Пожалуйста, введите город ")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if VkTools(acces_token).check_city(command.capitalize()):
                    self.message_send(event.user_id, "Город успешно установлен!")
                    self.params['city'] = command.capitalize()
                    return longpoll, True
                else:
                    self.message_send(event.user_id, "Такого города не существует. Пожалуйста, введите город")
                    return longpoll, False

    def input_bdate(self, event, longpoll):
        self.message_send(event.user_id, "Пожалуйста, укажите дату вашего рождения")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command.is_digit() == True and 1950 <= command <= 2007:
                    self.message_send(event.user_id, "Дата установлена!")
                    self.params['bdate'] = command.capitalize()
                    return longpoll, True
                else:
                    self.message_send(event.user_id, "Ошибка в дате рождения. Убедитесь, что дата является целым"
                                                     " четырехзначным числом!")
                    return longpoll, False

    def input_sex(self, event, longpoll):
        self.message_send(event.user_id, "Укажите пол (1 - женщина, 2 - мужчина)")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command.isdigit() == True and (command == '1' or command == '2'):
                    self.message_send(event.user_id, "Ваш пол установлен!")
                    self.params['sex'] = int(command)
                    return longpoll, True
                else:
                    self.message_send(event.user_id, "Ошибка при указании пола. Убедитесь, что вы ввели одну из цифр - "
                                                     "1, 2!")
                    return longpoll, False

    def input_status(self, event, longpoll):
        self.message_send(event.user_id, "Выберите ваш статус (1 - не женат/не замужем, 5 - "
                                         "всё сложно, 6 - в активном поиске)")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command.isdigit() == True and (command == '1' or command == '5' or command == '6'):
                    self.message_send(event.user_id, "Ваш статус установлен!")
                    self.params['relation'] = int(command)
                    return longpoll, True
                else:
                    self.message_send(event.user_id, "Ошибка в статусе. Убедитесь, что вы ввели одну из цифр - 1, 5, 6!")
                    return longpoll, False

    def get_list_profiles(self, event):
        self.users = self.vkapi.search_users(self.params, self.offset)
        self.counter = len(self.users)
        while len(self.users) != 0:
            user = self.users.pop()
            if check_user_in_profiles(user["id"]):
                self.counter -= 1
                continue
            else:
                attachment = self.vkapi.get_photos(user['id'])
                add_profile(user["id"], user["name"], get_id_db_user(event.user_id))
                self.message_send(event.user_id,
                                  f'Имя - {user["name"]}, ссылка: vk.com/id{user["id"]}',
                                  attachment=','.join(attachment)
                                  )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        is_True = False
        is_all_data = False
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command.capitalize() == 'Привет':
                    BotInterface.greeting(self, event)
                elif command.capitalize() == 'Поиск':
                    self.message_send(event.user_id, 'Прежде чем начать поиск, проверим, все ли ваши данные '
                                                     'были получены.')
                    if check_bot_user(event.user_id):
                        self.params = self.vkapi.get_profile_info(event.user_id)
                    else:
                        add_bot_user(event.user_id)

                    while is_all_data is False:
                        if self.params['city'] is None:
                            while is_True is False:
                                longpoll, is_True = self.input_city(event, longpoll)
                            is_True = False
                        if self.params['bdate'] is None:
                            while is_True is False:
                                longpoll, is_True = self.input_bdate(event, longpoll)
                            is_True = False
                        if self.params['sex'] is None:
                            while is_True is False:
                                longpoll, is_True = self.input_sex(event, longpoll)
                            is_True = False
                        if self.params['relation'] not in [1, 5, 6]:
                            while is_True is False:
                                longpoll, is_True = self.input_status(event, longpoll)
                            is_True = False
                        is_all_data = True

                    self.message_send(event.user_id, f'Ищу подходящие пары... ')
                    self.get_list_profiles(event)
                    self.offset += 30
                    while self.counter == 0:
                        self.get_list_profiles(event)
                    else:
                        self.message_send(event.user_id, 'Поиск завершен.')
                elif command.capitalize() == 'Пока':
                    self.message_send(event.user_id, 'Пока-пока!')
                    break
                else:
                    self.message_send(event.user_id, 'К сожалению, команда не опознана!')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()


