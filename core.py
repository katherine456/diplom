from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from config import acces_token

class VkTools():
    def __init__(self, acces_token):
        self.vkapi = vk_api.VkApi(token=acces_token)

    def get_age_from_year(self, bdate):
        return datetime.now().year - int(bdate.split('.')[2])

    def check_city(self, city):

        check_city = self.vkapi.method('users.search', {'hometown': city, 'count': 1})
        if check_city['items'] and city.isalpha() is True:
            return True
        else:
            return False

    def get_profile_info(self, user_id):

        try:
            info, = self.vkapi.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city, bdate, sex, relation'
                                 }
                                )
        except ApiError as e:
            info = {}
            print(f'Error = {e}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info
                                                                          and 'last_name' in info else None,
                     'id': info['id'],
                     'city': info.get('city')['title'] if info.get('city') is not None else None,
                     'bdate': self.get_age_from_year(info.get('bdate')),
                     'sex': info.get('sex') if info.get('sex') in info else None,
                     'relation': info.get('relation')
                     }
        return user_info

    def search_users(self, params, offset):
        try:
            users = self.vkapi.method('users.search',
                                    {'count': 30,
                                     'offset': offset,
                                     'age_from': params['bdate'] - 5,
                                     'age_to': params['bdate'] + 10,
                                     'is_closed': 0,
                                     'can_access_closed': True,
                                     'sex': 1 if params['sex'] == 2 else 2,
                                     'hometown': params['city'],
                                     'status': 6,
                                     'has_photo': True
                                     }
                                    )
        except (ApiError, KeyError) as e:
            users = []
            print(f'Error = {e}')


        res = [{'name': item['first_name'] + ' ' + item['last_name'], 'id': item['id']} for item in users['items']
               if item['is_closed'] == False]

        return res

    def get_photos(self, user_id):
        try:
            photos = self.vkapi.method('photos.get',
                                       {'owner_id': user_id,
                                        'album_id': 'profile',
                                        'count': 10,
                                        'extended': 1,
                                        })
        except ApiError as e:
            photos = {}
            print(f'Error = {e}')

        users_photos = []

        for photo in photos['items']:
            users_photos.append({'owner_id': photo['owner_id'],
                        'id': f"photo{photo['owner_id']}_{photo['id']}",
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )
        if photos:
            lst = users_photos
            lst.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        result = []
        _counter = 0

        for item in lst:
            if len(lst) >= 3:
                result += [item['id']]
                _counter += 1
                if _counter == 3:
                    return result
            elif len(lst) < 3 and len(lst) != 0:
                result += [item['id']]
                if _counter < 3:
                    return result
            else:
                return 'Ошибка в получении 3-х первых фото пользователя'

if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(554973226)
    users = bot.search_users(params, datetime.now().microsecond % 10000000)
    print(datetime.now().microsecond)
    # _counter = 20
    #
    # while _counter != 0:
    #     user = users.pop()
    #     attachment = bot.get_photos(user['id'])
    #     print(','.join(attachment))
    #     _counter -= 1

