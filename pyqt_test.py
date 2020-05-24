import random
import time
import re

from PyQt5 import QtWidgets, QtCore, QtGui

from ToolsfeedModule import ToolsFeed as TFm
from simple_tab import TabWidget

class FilterWordThread(QtCore.QThread):
    percent_signal = QtCore.pyqtSignal(float)
    count_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def count_lines(self, filename, chunk_size=1 << 13):
        with open(filename) as file:
            return sum(chunk.count('\n')
                       for chunk in iter(lambda: file.read(chunk_size), ''))

    def filter_word(self, stop_words, file_in, file_out):
        reg = re.compile('[^a-zA-Zа-яА-Я ]')
        sleep = lambda x: time.sleep(x)
        users = api.rename(file_in)
        words_old = api.rename(stop_words)
        words = []

        count = 1
        max_count = self.count_lines(file_in)

        for word in words_old:
            words.append(word.lower())

        words = set(words)
        for user in users:
            try:
                user_biography = api.get_data(user, parameters=['biography'])
                user_biography = user_biography.lower()
                user_biography = reg.sub('', user_biography)
                user_biography = user_biography.split(' ')
            except KeyError:
                print(f'Пользователя {user} не существует, пропускаем')
                sleep(1)
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)
                count += 1
                continue

            user_biography = set(user_biography)

            if words.isdisjoint(user_biography):
                print(f'{user} не имеет стоп слов, добавляю')
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)
                api.writer_base(user, file=file_out)
                count += 1
                sleep(1)
            else:
                print(f'{user} есть в стоп листе, пропускаю')
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)
                count += 1

    def run(self):
        word = main_window.widget_filter_word.line_count.text()
        file_in = main_window.widget_filter_word.line_base.text()
        file_out = main_window.widget_filter_word.line_newbase.text()

        print(word)
        print(file_in)
        print(file_out)

        self.filter_word(word, file_in, file_out)



class FilterDayThread(QtCore.QThread):
    percent_signal = QtCore.pyqtSignal(float)
    count_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def count_lines(self, filename, chunk_size=1 << 13):
        with open(filename) as file:
            return sum(chunk.count('\n')
                       for chunk in iter(lambda: file.read(chunk_size), ''))

    def filter_day(self, day, file_in, file_out):
        one_day = 86400
        sleep = lambda x: time.sleep(x)
        users = api.rename(file_in)

        count = 1
        max_count = self.count_lines(file_in)

        for user in users:
            try:
                user_id = api.get_data(user)
            except KeyError:
                print(f'Пользователя {user} не существует, пропускаем')
                sleep(0.5)
                count += 1
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)
                continue
            api.getUserFeed(user_id)
            data_user = api.LastJson

            try:
                data_public = data_user['items'][0]['taken_at']
            except KeyError:
                print(f'Пользователь {user} является приватным, пропускаем')
                sleep(0.5)
                count += 1
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)

                continue
            except IndexError:
                print(f'У пользователя {user} нету публикаций, пропускаем')
                sleep(0.5)
                count += 1
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)

                continue

            data_now = time.time()
            data_duration = int((data_now - data_public) / one_day)

            if data_duration <= day:
                print(f'Последняя публикация пользователя {user} меньше {day} дней назад')
                print('Добавляем его в базу')
                api.writer_base(user, file=file_out)
                count += 1
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)

            else:
                print(f'Последняя публикация пользователя {user} больше {day} дней назад, пропускаю')
                count += 1
                self.count_signal.emit(str(count), str(max_count))
                percent = count / max_count * 100
                self.percent_signal.emit(percent)

            sleep(0.5)

    def run(self):
        day = int(main_window.widget_filter_day.line_count.text())
        file_in = main_window.widget_filter_day.line_base.text()
        file_out = main_window.widget_filter_day.line_newbase.text()

        print(day)
        print(file_in)
        print(file_out)

        self.filter_day(day, file_in, file_out)


class UnfollowingThread(QtCore.QThread):
    percent_signal = QtCore.pyqtSignal(float)
    count_signal = QtCore.pyqtSignal(str)
    count_max_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def unfollow(self, whitelist='', time_min=0, time_max=1):

        followings = api.get_followings()

        if whitelist:
            whitelist = api.rename(whitelist)

        max_count_unfollowing = len(followings)
        self.count_max_signal.emit(max_count_unfollowing)

        count = 1
        for user in followings:
            if user in whitelist:
                print(f'{user} в белом листе, пропускаю')
                count += 1
                continue
            user_id = api.get_data(user)
            api.unfollow(user_id)
            print(f'отписка от {user}')

            percent = count / max_count_unfollowing * 100
            print(percent)
            self.percent_signal.emit(percent)
            self.count_signal.emit(str(count))
            self.sleep(random.randint(time_min, time_max))
            count += 1

        print('Все отписки совершены')

    def run(self):
        min = int(main_window.widget_unfollowing.line_min.text())
        max = int(main_window.widget_unfollowing.line_max.text())
        whitelist = main_window.widget_unfollowing.line_base.text()
        self.unfollow(whitelist, min, max)


class FollowingThread(QtCore.QThread):
    percent_signal = QtCore.pyqtSignal(int)
    count_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def change_file(self, file, str):
        with open(file, 'w') as f:
            f.write(str)

    def following(self, file, count, time_min=0, time_max=1, like=True, private=False):

        print('following')
        users = set(api.rename(file))
        followings = set(api.get_followings())
        not_followings = list(users - followings)
        counter = 1

        while True:
            try:
                if counter == count + 1:
                    break
                user = not_followings.pop(0)
                string = '\n'.join(not_followings)
                self.change_file(file, string)
                print('Забрал самый верх')
                while True:
                    try:
                        data = api.get_data(user, parameters=['pk', 'is_private'])
                    except:
                        print(f"Пользователя {user} не существует")
                        user = not_followings.pop(0)
                        string = '\n'.join(not_followings)
                        self.change_file(file, string)
                        print('Забрал середина')

                        continue
                    if data[1]:
                        if private:
                            user_id = data[0]
                            break
                        else:
                            print(f'{user} являеется приватным аккаунтом, пропускаем!')
                            user = not_followings.pop(0)
                            string = '\n'.join(not_followings)
                            self.change_file(file, string)
                            print('Забрал низ')

                    else:
                        user_id = data[0]
                        break

                api.follow(user_id)
                print(f'Подписка на {user} совершена!')
                if like:
                    api.getUserFeed(user_id)
                    feed_user = api.LastJson
                    feed_id = feed_user['items'][0]['id']
                    api.like(feed_id)

                percent = counter / count * 100
                self.percent_signal.emit(percent)
                self.count_signal.emit(counter)
                counter += 1
                self.sleep(random.randint(time_min, time_max))
            except IndexError:
                print('База закончилась!')
                break

        return print('Все подписки совершены')

    def run(self):
        base_following = main_window.widget_following.line_base.text()
        count_following = int(main_window.widget_following.line_count.text())
        min_following = int(main_window.widget_following.line_min.text())
        max_following = int(main_window.widget_following.line_max.text())
        print('run')
        print(base_following)
        print(count_following)
        print(min_following)
        print(max_following)

        self.following(base_following, count_following, time_min=min_following, time_max=max_following)


class LoginWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.resize(300, 100)
        self.setWindowTitle('ToolsFeed-login')
        self.label_login = QtWidgets.QLabel('Введите логин')
        self.line_login = QtWidgets.QLineEdit('')

        self.label_password = QtWidgets.QLabel('Введите пароль')
        self.line_password = QtWidgets.QLineEdit('')
        self.line_password.setEchoMode(2)

        self.label_device_id = QtWidgets.QLabel('Введите ID устройства')
        self.line_device_id = QtWidgets.QLineEdit()

        self.label_error = QtWidgets.QLabel('Не корректные данные')
        self.label_error.setAlignment(QtCore.Qt.AlignHCenter)

        self.button = QtWidgets.QPushButton('Вход')
        self.button.clicked.connect(self.submit_login)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.label_login)
        self.vbox.addWidget(self.line_login)
        self.vbox.addWidget(self.label_password)
        self.vbox.addWidget(self.line_password)
        self.vbox.addWidget(self.label_device_id)
        self.vbox.addWidget(self.line_device_id)

        self.vbox.addWidget(self.button)

        self.setLayout(self.vbox)

    def submit_login(self):
        global api

        login = self.line_login.text()
        password = self.line_password.text()

        api = TFm(login, password)

        if self.line_device_id.text():
            api.device_id = f'android-{self.line_device_id.text()}'

        if api.login():
            self.setHidden(True)
            main_window.setHidden(False)
        else:
            self.update()
            self.vbox.addWidget(self.label_error)


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setHidden(True)

        self.resize(300, 100)

        # ---------------Менюбар-----------

        self.change_account_menubar = QtWidgets.QAction('Сменить аккаунт')
        self.change_account_menubar.triggered.connect(self.change_account)

        self.menubar = QtWidgets.QMenuBar()

        self.action_menu = self.menubar.addMenu('Действие')
        self.action_menu.addAction(self.change_account_menubar)

        # ---------------END Менюбар-------

        self.tab = QtWidgets.QTabWidget()

        # ---------------Tab1-----------
        """"Тут все виджеты для колонки подписок"""

        self.widget_following = TabWidget()
        self.widget_following.thread = FollowingThread()

        self.widget_following.timer = QtCore.QTimer()
        self.widget_following.timer.timeout.connect(self.timer_following)

        self.widget_following.btn_start.clicked.connect(self.clicked_following)
        self.widget_following.thread.started.connect(self.start_following)
        self.widget_following.thread.finished.connect(self.finished_following)
        self.widget_following.thread.percent_signal.connect(self.change_percent_following, QtCore.Qt.QueuedConnection)
        self.widget_following.thread.count_signal.connect(self.change_count_following, QtCore.Qt.QueuedConnection)

        self.widget_following.btn_cancel.clicked.connect(self.clicked_cancel_following)

        self.widget_following.btn_base.clicked.connect(self.open_base_following)

        self.tab.addTab(self.widget_following, '&Following')

        # ----------------End Tab1----------------------

        # ----------------Tab2--------------------------
        """"Тут все виджеты для колонки отписок"""

        self.widget_unfollowing = TabWidget()
        self.widget_unfollowing.thread = UnfollowingThread()
        self.widget_unfollowing.timer = QtCore.QTimer()
        self.widget_unfollowing.timer.timeout.connect(self.timer_unfollowing)

        self.widget_unfollowing.label_about = QtWidgets.QLabel("Полная отписка от всех!\nКроме белой базы")
        self.widget_unfollowing.label_about.setAlignment(QtCore.Qt.AlignHCenter)
        self.widget_unfollowing.vbox_all.insertWidget(0, self.widget_unfollowing.label_about)

        self.widget_unfollowing.label_base.setText("Белый лист:")
        self.widget_unfollowing.btn_base.clicked.connect(self.open_white_unfollowing)

        self.widget_unfollowing.label_count.hide()
        self.widget_unfollowing.line_count.hide()

        self.widget_unfollowing.btn_start.clicked.connect(self.clicked_unfollowing)
        self.widget_unfollowing.thread.started.connect(self.start_unfollowing)
        self.widget_unfollowing.thread.finished.connect(self.finished_unfollowing)
        self.widget_unfollowing.thread.count_max_signal.connect(self.change_max_count_unfollofing,
                                                                QtCore.Qt.QueuedConnection)
        self.widget_unfollowing.thread.count_signal.connect(self.change_count_unfollowing, QtCore.Qt.QueuedConnection)
        self.widget_unfollowing.thread.percent_signal.connect(self.change_percent_unfollowing,
                                                              QtCore.Qt.QueuedConnection)
        self.widget_unfollowing.btn_cancel.clicked.connect(self.clicked_cancel_unfollowing)

        self.tab.addTab(self.widget_unfollowing, '&Unfollowing')

        # ----------------End Tab2----------------------

        # ----------------Tab3--------------------------

        self.widget_filter_day = TabWidget()
        self.widget_filter_day.thread = FilterDayThread()

        self.widget_filter_day.timer = QtCore.QTimer()
        self.widget_filter_day.timer.timeout.connect(self.timer_filter_day)

        self.widget_filter_day.label_base.setText("База для фильтрации:")
        self.widget_filter_day.btn_base.clicked.connect(self.open_base_filter_day)

        self.widget_filter_day.label_newbase = QtWidgets.QLabel('Название новой базы:')
        self.widget_filter_day.line_newbase = QtWidgets.QLineEdit()

        self.widget_filter_day.hbox_newbase = QtWidgets.QHBoxLayout()
        self.widget_filter_day.hbox_newbase.addWidget(self.widget_filter_day.label_newbase)
        self.widget_filter_day.hbox_newbase.addWidget(self.widget_filter_day.line_newbase)

        self.widget_filter_day.vbox_all.insertLayout(1, self.widget_filter_day.hbox_newbase)

        self.widget_filter_day.label_count.setText('Количество дней:')

        self.widget_filter_day.label_time.hide()
        self.widget_filter_day.line_min.hide()
        self.widget_filter_day.line_max.hide()

        self.widget_filter_day.btn_start.clicked.connect(self.clicked_start_filter_day)
        self.widget_filter_day.btn_cancel.clicked.connect(self.clicked_cancel_filter_day)

        self.widget_filter_day.thread.started.connect(self.start_filter_day)
        self.widget_filter_day.thread.finished.connect(self.finished_filter_day)
        self.widget_filter_day.thread.count_signal.connect(self.change_count_filter_day, QtCore.Qt.QueuedConnection)
        self.widget_filter_day.thread.percent_signal.connect(self.change_percent_filter_day,
                                                             QtCore.Qt.QueuedConnection)

        self.tab.addTab(self.widget_filter_day, 'Filter &day')

        # ----------------End Tab3----------------------

        # ----------------End Tab4----------------------

        self.widget_filter_word = TabWidget()
        self.widget_filter_word.thread = FilterWordThread()

        self.widget_filter_word.timer = QtCore.QTimer()
        self.widget_filter_word.timer.timeout.connect(self.timer_filter_word)

        self.widget_filter_word.label_base.setText("База для фильтрации:")
        self.widget_filter_word.btn_base.clicked.connect(self.open_base_filter_word)

        self.widget_filter_word.label_newbase = QtWidgets.QLabel('Название новой базы:')
        self.widget_filter_word.line_newbase = QtWidgets.QLineEdit()


        self.widget_filter_word.hbox_newbase = QtWidgets.QHBoxLayout()
        self.widget_filter_word.hbox_newbase.addWidget(self.widget_filter_word.label_newbase)
        self.widget_filter_word.hbox_newbase.addWidget(self.widget_filter_word.line_newbase)

        self.widget_filter_word.vbox_all.insertLayout(2, self.widget_filter_word.hbox_newbase)

        self.widget_filter_word.label_count.setText('База слов:')
        self.widget_filter_word.btn_count = QtWidgets.QPushButton('Открыть')
        self.widget_filter_word.hbox_count.addWidget(self.widget_filter_word.btn_count)
        self.widget_filter_word.btn_count.clicked.connect(self.open_word_filter_word)



        self.widget_filter_word.label_time.hide()
        self.widget_filter_word.line_min.hide()
        self.widget_filter_word.line_max.hide()

        self.widget_filter_word.btn_start.clicked.connect(self.clicked_start_filter_word)
        self.widget_filter_word.btn_cancel.clicked.connect(self.clicked_cancel_filter_word)

        self.widget_filter_word.thread.started.connect(self.start_filter_word)
        self.widget_filter_word.thread.finished.connect(self.finished_filter_word)
        self.widget_filter_word.thread.count_signal.connect(self.change_count_filter_word, QtCore.Qt.QueuedConnection)
        self.widget_filter_word.thread.percent_signal.connect(self.change_percent_filter_word,
                                                             QtCore.Qt.QueuedConnection)

        self.tab.addTab(self.widget_filter_word, 'Filter &words')
        # ----------------End Tab4----------------------


        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.menubar)
        self.vbox.addWidget(self.tab)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vbox)

    # ------------- MEU FUNC----------------------------------------

    def change_account(self):
        self.setHidden(True)
        login_window.setHidden(False)

    # ------------- MENU FUNC END-----------------------------------

    # ------------- Tab1 FUNC----------------------------------------
    def open_base_following(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        print(file_path)
        self.widget_following.line_base.setText(file_path[0])

    def clicked_following(self):
        self.widget_following.btn_start.setDisabled(True)
        self.widget_following.btn_cancel.setDisabled(False)
        print('start')
        self.widget_following.thread.start()

    def clicked_cancel_following(self):
        print('cancel')
        self.widget_following.thread.terminate()
        self.widget_following.btn_cancel.setDisabled(True)

    def start_following(self):
        self.widget_following.step_timer = 0
        self.widget_following.timer.start(1000)

        self.widget_following.label_timer.show()
        self.widget_following.label_start.show()
        self.widget_following.pbar.show()

    def finished_following(self):
        print('finished')
        self.widget_following.pbar.hide()
        self.widget_following.label_start.hide()
        self.widget_following.label_timer.hide()

        self.widget_following.btn_start.setDisabled(False)
        self.widget_following.timer.stop()

        self.widget_following.step_timer = 0

    def change_percent_following(self, e):
        print('percent')
        self.widget_following.pbar.setValue(e)

    def change_count_following(self, e):
        print('count')
        count_follow = self.widget_following.line_count.text()
        self.widget_following.label_start.setText(f'Подписки {e}/{count_follow}')

    def timer_following(self):
        print('timer')
        count = time.gmtime(self.widget_following.step_timer)
        timer = time.strftime("%H:%M:%S", count)
        self.widget_following.label_timer.setText(f'Времени прошло: {timer}')
        self.widget_following.step_timer += 1

    # -------------END Tab1 FUNC----------------------------------------

    # ------------- Tab2 FUNC----------------------------------------
    def open_white_unfollowing(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        self.widget_unfollowing.line_base.setText(file_path[0])

    def clicked_unfollowing(self):
        self.widget_unfollowing.btn_start.setDisabled(True)
        self.widget_unfollowing.btn_cancel.setDisabled(False)
        self.widget_unfollowing.thread.start()

    def clicked_cancel_unfollowing(self):
        self.widget_unfollowing.thread.terminate()
        self.widget_unfollowing.btn_cancel.setDisabled(True)

    def start_unfollowing(self):
        self.widget_unfollowing.max_count = 0
        self.widget_unfollowing.step_timer = 0
        self.widget_unfollowing.timer.start(1000)
        self.widget_unfollowing.label_start.show()
        self.widget_unfollowing.label_timer.show()
        self.widget_unfollowing.pbar.show()

    def finished_unfollowing(self):
        self.widget_unfollowing.pbar.hide()
        self.widget_unfollowing.label_start.hide()
        self.widget_unfollowing.label_timer.hide()
        self.widget_unfollowing.btn_start.setDisabled(False)
        self.widget_unfollowing.timer.stop()

    def change_max_count_unfollofing(self, e):
        self.widget_unfollowing.max_count = e

    def change_percent_unfollowing(self, e):
        self.widget_unfollowing.pbar.setValue(e)

    def change_count_unfollowing(self, e):
        count = self.widget_unfollowing.max_count
        self.widget_unfollowing.label_start.setText(f'Отписки: {e}/{count}')

    def timer_unfollowing(self):
        count = time.gmtime(self.widget_unfollowing.step_timer)
        timer = time.strftime("%H:%M:%S", count)
        self.widget_unfollowing.label_timer.setText(f'Времени прошло: {timer}')
        self.widget_unfollowing.step_timer += 1

    # -------------END Tab2 FUNC----------------------------------------

    # -------------END Tab3 FUNC----------------------------------------
    def open_base_filter_day(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        print(file_path)
        self.widget_filter_day.line_base.setText(file_path[0])

    def clicked_start_filter_day(self):
        self.widget_filter_day.btn_start.setDisabled(True)
        self.widget_filter_day.btn_cancel.setDisabled(False)
        self.widget_filter_day.thread.start()

    def clicked_cancel_filter_day(self):
        self.widget_filter_day.btn_start.setDisabled(False)
        self.widget_filter_day.btn_cancel.setDisabled(True)
        self.widget_filter_day.thread.terminate()

    def start_filter_day(self):
        self.widget_filter_day.step_timer = 0
        self.widget_filter_day.timer.start(1000)
        self.widget_filter_day.label_timer.show()
        self.widget_filter_day.label_start.show()
        self.widget_filter_day.pbar.show()

    def finished_filter_day(self):
        self.widget_filter_day.pbar.hide()
        self.widget_filter_day.label_start.hide()
        self.widget_filter_day.label_timer.hide()
        self.widget_filter_day.btn_start.setDisabled(False)
        self.widget_filter_day.timer.stop()
        self.widget_filter_day.step_timer = 0

    def change_percent_filter_day(self, e):
        self.widget_filter_day.pbar.setValue(e)

    def change_count_filter_day(self, e, max_user):
        self.widget_filter_day.label_start.setText(f'Фильтр: {e}/{max_user}')

    def timer_filter_day(self):
        count = time.gmtime(self.widget_filter_day.step_timer)
        timer = time.strftime("%H:%M:%S", count)
        self.widget_filter_day.label_timer.setText(f'Времени прошло: {timer}')
        self.widget_filter_day.step_timer += 1

    # -------------END Tab3 FUNC----------------------------------------

    # -------------Tab4 FUNC----------------------------------------

    def open_base_filter_word(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        self.widget_filter_word.line_base.setText(file_path[0])

    def open_word_filter_word(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        self.widget_filter_word.line_count.setText(file_path[0])

    def clicked_start_filter_word(self):
        self.widget_filter_word.btn_start.setDisabled(True)
        self.widget_filter_word.btn_cancel.setDisabled(False)
        self.widget_filter_word.thread.start()

    def clicked_cancel_filter_word(self):
        self.widget_filter_word.btn_start.setDisabled(False)
        self.widget_filter_word.btn_cancel.setDisabled(True)
        self.widget_filter_word.thread.terminate()

    def start_filter_word(self):
        self.widget_filter_word.step_timer = 0
        self.widget_filter_word.timer.start(1000)
        self.widget_filter_word.label_timer.show()
        self.widget_filter_word.label_start.show()
        self.widget_filter_word.pbar.show()

    def finished_filter_word(self):
        self.widget_filter_word.pbar.hide()
        self.widget_filter_word.label_start.hide()
        self.widget_filter_word.label_timer.hide()
        self.widget_filter_word.btn_start.setDisabled(False)
        self.widget_filter_word.timer.stop()
        self.widget_filter_word.step_timer = 0

    def change_percent_filter_word(self, e):
        self.widget_filter_word.pbar.setValue(e)

    def change_count_filter_word(self, e, max_user):
        self.widget_filter_word.label_start.setText(f'Фильтр: {e}/{max_user}')

    def timer_filter_word(self):
        count = time.gmtime(self.widget_filter_word.step_timer)
        timer = time.strftime("%H:%M:%S", count)
        self.widget_filter_word.label_timer.setText(f'Времени прошло: {timer}')
        self.widget_filter_word.step_timer += 1

    # -------------END Tab4 FUNC----------------------------------------


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon1.ico'))
    login_window = LoginWindow()
    login_window.show()

    main_window = MainWindow()

    sys.exit(app.exec_())
