# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from magnet2torrent import *
from torrent2magnet import *
import os
import sys
import sip
import string

reload(sys)
sys.setdefaultencoding('UTF-8')

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class WorkThread(QThread):
    """command: [command, [params]]"""
    finishSignal = pyqtSignal(dict)
    def __init__(self, command, parent=None):
        super(WorkThread, self).__init__(parent)
        self.command = command

    def run(self):
        if self.command[0]== 'magent2torrent':
            magnet = str(self.command[1])
            filename = self.command[2]
            torrent = magnet2torrent_cache(magnet, filename)
            if torrent:
                data = {'status': 0, 'result': torrent}
            else:
                torrent = magnet2torrent_libtorrent(magnet, filename)
                if torrent:
                    data = {'status': 0, 'result': torrent}
                else:
                    data = {'status': 1, 'result': ''}
        if self.command[0] == 'torrent2magent':
            magnet = torrent2magnet_libtorrent(self.command[1])
            if magnet:
                data = {'status': 0, 'result': magnet}
            else:
                data = {'status': 1, 'result': ''}
            
        self.finishSignal.emit(data)

class Main(QWidget):
    def __init__(self,parent=None):
        super(Main, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.tr("磁力种子转换工具"))
        self.resize(400, 100)
        self.setWindowIcon(QIcon('bittorrent.ico'))
        self.center()

        magnetLabel = QLabel(self.tr("磁力转种子"))
        self.magnetLineEdit = QLineEdit()
        self.magnetLineEdit.setMaximumWidth(350)
        self.magnetLineEdit.setFixedWidth(350)
        self.magnetPushButton = QPushButton(self.tr("转换"))

        magnetLayout = QHBoxLayout()
        magnetLayout.addStretch()
        magnetLayout.addWidget(magnetLabel)
        magnetLayout.addWidget(self.magnetLineEdit)
        magnetLayout.addWidget(self.magnetPushButton)

        torrentLabel = QLabel(self.tr("种子转磁力"))
        self.torrentLineEdit = QLineEdit()
        self.torrentLineEdit.setMaximumWidth(350)
        self.torrentLineEdit.setFixedWidth(350)
        self.torrentPushButton = QPushButton(self.tr("选择"))

        torrentLayout = QHBoxLayout()
        torrentLayout.addStretch()
        torrentLayout.addWidget(torrentLabel)
        torrentLayout.addWidget(self.torrentLineEdit)
        torrentLayout.addWidget(self.torrentPushButton)

        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(15)
        mainLayout.setSpacing(10)
        mainLayout.addLayout(magnetLayout)
        mainLayout.addLayout(torrentLayout)

        self.connect(self.magnetPushButton, SIGNAL('clicked()'), self.magnetWork)
        self.connect(self.torrentPushButton, SIGNAL('clicked()'), self.torrentWork)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def magnetWork(self):
        magnet = self.magnetLineEdit.text()
        if magnet:
            self.magnetPushButton.setDisabled(True)
            filename = unicode(QFileDialog.getSaveFileName(self, 'Save File', '', ".torrent(*.torrent)"))
            self.magnetWorkThread = WorkThread(['magent2torrent', magnet, filename])
            self.magnetWorkThread.finishSignal.connect(self.magnetWorkEnd)
            self.magnetWorkThread.start()
        else:
            QMessageBox.information(self, self.tr("提示"), self.tr("未输入任何东西！"))

    def magnetWorkEnd(self, data):
        self.magnetPushButton.setDisabled(False)
        if data['status']:
            QMessageBox.information(self, self.tr("提示"), self.tr("转换失败！"))
        else:
            QMessageBox.information(self, self.tr("提示"), self.tr("转换成功！"))

    def torrentWork(self):
        filename = unicode(QFileDialog.getOpenFileName(self, 'Open file', './', "All Files (*);;Torrent Files (*.torrent)"))
        if filename:
            self.torrentPushButton.setDisabled(True)
            self.torrentWorkThread = WorkThread(['torrent2magent', filename])
            self.torrentWorkThread.finishSignal.connect(self.torrentWorkEnd)
            self.torrentWorkThread.start()
        else:
            QMessageBox.information(self, self.tr("提示"), self.tr("未选择任何文件！"))

    def torrentWorkEnd(self, data):
        self.torrentPushButton.setDisabled(False)
        if data['status']:
            QMessageBox.information(self, self.tr("提示"), self.tr("转换失败！"))
        else:
            self.torrentLineEdit.setText(data['result'])
            self.torrentLineEdit.setCursorPosition(0)
            QMessageBox.information(self, self.tr("提示"), self.tr("转换成功！"))
            

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = Main()
    main.show()

    sip.setdestroyonexit(False)
    sys.exit(app.exec_())