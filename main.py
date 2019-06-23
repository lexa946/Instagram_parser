from InstagramAPI import InstagramAPI
import requests
import random
import time
import re



class ToolsFeed(InstagramAPI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_data(self, user, parameters=['pk']):
        '''
        Получаем данные пользователя
        :param user: Имя инстаграмма
        :param data: Передаем что хотим получить (pk, biography, full_name, is_private)
        :return: Возвращает список запрошенных данных, либо None если не удалось найти аккаунт (По умолчанию: ID)
        '''
        try:
            self.searchUsername(user)
            json = self.LastJson
        except:
            return None

        data = []
        default_parameters = {'pk', 'biography', 'full_name', 'is_private'}

        for param in parameters:
            if param in default_parameters:
                data.append(json['user'][param])

        if len(data) == 1:
            return data[0]


        return data


    def get_all_id(self, file): # Доделать
        all_id = []
        limit = 1
        users = self.rename(file)

        while True:


            for user in users:
                try:
                    user = user.rstrip()
                    id = self.get_id(user)
                    all_id.append(id)
                    time.sleep(0.7)


                    # if limit%80 != 0:
                    #     limit +=1
                    #     print(limit)
                    # else:
                    #     print('Delay 15 second')
                    #     limit +=1
                    #     print(limit)
                    #     for i in tqdm(range(15)):
                    #         time.sleep(1)
                except:
                    print("don't search: ", user)
        return all_id

    def rename(self, file):
        '''
        Удаляет все пробелы и символы переноса строки у имен
        :param file: .txt файл с именами в столбик
        :return: Возвращает отформатированный список имен
        '''
        data = []
        with open(file+'.txt') as file:
            for user in file:
                user = user.rstrip()
                data.append(user)
            return data

    def writer_base(self, data, file):
        '''
        Записываем данные в файл
        :param data: Что записывать(пользователи)
        :param file: как назовем файл
        :return:
        '''
        with open(file+'.txt', 'a') as f:
            f.write(data+'\n')

    def get_followings(self):
        '''
        Получить словарь с именами и ID
        :return: Возвращает словарь Имя:ID
        '''
        self.getSelfUsersFollowing()
        json = self.LastJson
        followings = []
        for user in json['users']:
            followings.append(user['username'])
        return followings


    def following(self, file, count, time_min=0, time_max=1, private=False):
        '''
        Делаем подписки на не подписанные аккаунты
        :param data: список имен
        :param count: сколько делать подписок
        :param time_min: минимальная задержка
        :param time_max: максимвльная задержка
        :param private: включить подписку на приватные аккаунты, либо нет (По умолчанию: нет)
        :return:
        '''
        users = set(self.rename(file))
        followings = set(self.get_followings())
        not_followings = list(users - followings)
        counter = 0
        while True:
            try:
                if counter == count:
                    break
                user = not_followings.pop(0)
                while True:
                    try:
                        data = self.get_data(user, parameters=['pk', 'is_private'])
                    except:
                        print(f"Пользователя {user} не существует")
                        user = not_followings.pop(0)
                        continue
                    if data[1]:
                        if private:
                            user_id = data[0]
                            break
                        else:
                            print(f'{user} являеется приватным аккаунтом, пропускаем!')
                            user = not_followings.pop(0)
                    else:
                        user_id = data[0]
                        break

                self.follow(user_id)
                print(f'Подписка на {user} совершена!')
                counter += 1
                time.sleep(random.randint(time_min, time_max))
            except IndexError:
                print('База закончилась!')
                break

        return print('Все подписки совершены')

    def download_all_video(self, user):
        '''
        Скачивает все видео с аккаунта
        :param user: имя аккаунта
        :return:
        '''
        increment = 0
        id = self.get_data(user)
        feeds = self.getTotalUserFeed(id)
        for i in feeds:
            try:
                url = i['video_versions'][0]['url']
            except:
                continue
            response = requests.get(url)
            with open(f'video_{str(increment)}.mp4', 'wb') as file:
                file.write(response.content)
            increment += 1
            time.sleep(1)
            print(f"Загрузка видео номер - {increment}")
        return print('Все видеофайлы загружены!')

    def filter_data_for_day(self, count,file_in='',file_out=''):
        '''
        Фильтруем базу по дате последнего поста
        :param count: сколько дней назад
        :param file_in: Название файла с базой, которую будем фильтровать
        :param file_out: Название файла, куда будут записываться отфильтрованные пользователи
        :return:
        '''
        one_day = 86400
        sleep = lambda x: time.sleep(x)
        users = self.rename(file_in)
        for user in users:
            try:
                user_id = self.get_data(user)
            except KeyError:
                print(f'Пользователя {user} не существует, пропускаем')
                sleep(0.5)
                continue
            self.getUserFeed(user_id)
            data_user = self.LastJson

            try:
                data_public = data_user['items'][0]['taken_at']
            except KeyError:
                print(f'Пользователь {user} является приватным, пропускаем')
                sleep(0.5)
                continue
            except IndexError:
                print(f'У пользователя {user} нету публикаций, пропускаем')
                sleep(0.5)
                continue

            data_now = time.time()
            data_duration = int((data_now - data_public) / one_day)

            if data_duration <= count:
                print(f'Последняя публикация пользователя {user} меньше {count} дней назад')
                print('Добавляем его в базу')
                self.writer_base(user,file=file_out)
            else:
                print(f'Последняя публикация пользователя {user} больше {count} дней назад, пропускаю')
            sleep(0.5)



    def filter_data_for_words(self, stop_words = '', file_in='', file_out=''):
        '''
        Фильтрует пользователей по стоп словам
        :param stop_words: база стоп слов
        :param file_in: база имен инстаграм
        :param file_out: файл в который записывать валидных пользователей
        :return:
        '''

        reg = re.compile('[^a-zA-Zа-яА-Я ]')
        sleep = lambda x: time.sleep(x)
        users = self.rename(file_in)
        words_old = self.rename(stop_words)
        words = []

        for word in words_old:
            words.append(word.lower())

        words = set(words)
        for user in users:
            try:
                user_biography = self.get_data(user, parameters=['biography'])
                user_biography = user_biography.lower()
                user_biography = reg.sub('', user_biography)
                user_biography = user_biography.split(' ')
            except KeyError:
                print(f'Пользователя {user} не существует, пропускаем')
                sleep(1)
                continue

            user_biography = set(user_biography)

            if words.isdisjoint(user_biography):
                print(f'{user} не имеет стоп слов, добавляю')
                self.writer_base(user, file=file_out)
                sleep(1)
            else:
                print(f'{user} есть в стоп листе, пропускаю')

def main():

    # api.download_all_video('run_vine') пример парсинга видео
    # api.following('volchara.txt', 800, time_min=120, time_max=130) #Пример фоловинга
    # api.get_dict_followings()
    # data = api.get_data('go_na_butilku', parameters=['full_name', 'pk', 'is_private'])  # Пример атрибутов инстаграмма
    # api.filter_data_for_day(5, file_in='name', file_out='date_of_5')# Пример фльтра
    # volchara_ebuchiy: Vo2019ra
    # dunkan_makridi Du2019an

    api = ToolsFeed("dunkan_makridi", "Du2019an")
    if api.login():

        bio = api.filter_data_for_day(7,file_in='filter_words', file_out='filter_all_for_7_days')


    else:
        print("Can't login!")


if __name__ == '__main__':
    start_time = time.time()
    main()
    time_duration = time.time() - start_time
    print(f'--- {time_duration} seconds ---')


    # constr = {'Ken', 'Baby', 'Lock', 'Alex', 'Job', 'Peter', 'Keny',1}
    # constr2 = {'Ken', 'Lock', 'Job', 'Peter', 'Keny'}
    # constr3 = constr - constr2
    # print(constr3)
