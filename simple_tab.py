from PyQt5 import QtCore, QtWidgets, QtGui

class TabWidget(QtWidgets.QWidget):
    ''' болванка под табы'''
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.label_base = QtWidgets.QLabel('Название базы:')
        self.line_base = QtWidgets.QLineEdit()
        self.btn_base = QtWidgets.QPushButton('Открыть')

        self.hbox_base = QtWidgets.QHBoxLayout()
        self.hbox_base.addWidget(self.label_base)
        self.hbox_base.addWidget(self.line_base)
        self.hbox_base.addWidget(self.btn_base)

        self.label_count = QtWidgets.QLabel('Количество подписок:')
        self.line_count = QtWidgets.QLineEdit()
        self.hbox_count = QtWidgets.QHBoxLayout()
        self.hbox_count.addWidget(self.label_count)
        self.hbox_count.addWidget(self.line_count)

        self.label_time = QtWidgets.QLabel('Мин\Макс задержка:')
        self.line_min = QtWidgets.QLineEdit()
        self.line_max = QtWidgets.QLineEdit()

        self.hbox_time = QtWidgets.QHBoxLayout()
        self.hbox_time.addWidget(self.label_time)
        self.hbox_time.addWidget(self.line_min)
        self.hbox_time.addWidget(self.line_max)

        self.btn_start = QtWidgets.QPushButton('Начать')
        self.btn_cancel = QtWidgets.QPushButton("Отмена")
        self.btn_cancel.setDisabled(True)

        self.hbox_btn = QtWidgets.QHBoxLayout()
        self.hbox_btn.addWidget(self.btn_start)
        self.hbox_btn.addWidget(self.btn_cancel)

        self.label_timer = QtWidgets.QLabel('Таймер')
        self.label_start = QtWidgets.QLabel('Началось')
        self.label_timer.hide()
        self.label_start.hide()

        self.hbox_progress = QtWidgets.QHBoxLayout()
        self.hbox_progress.addWidget(self.label_start)
        self.hbox_progress.addWidget(self.label_timer)

        self.pbar = QtWidgets.QProgressBar()
        self.pbar.hide()

        self.vbox_all = QtWidgets.QVBoxLayout()
        self.vbox_all.addLayout(self.hbox_base)
        self.vbox_all.addLayout(self.hbox_count)
        self.vbox_all.addLayout(self.hbox_time)
        self.vbox_all.addLayout(self.hbox_btn)
        self.vbox_all.addLayout(self.hbox_progress)
        self.vbox_all.addWidget(self.pbar)


        self.setLayout(self.vbox_all)