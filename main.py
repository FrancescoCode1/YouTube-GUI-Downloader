import traceback
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QFileDialog, QListView, QListWidget, QListWidgetItem, QRadioButton
import pytube
import os
from qt_material import apply_stylesheet

def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)

#Signals are used to pass data or states to the main thread. Finished is a state, error contains a touple defined below, result contains data returned by the function
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


#Worker class keeps long operations from making it impossible to interact with the gui
#fn contains the function that else blocks the event loop
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.fn = fn
        self.signals = WorkerSignals()

    #this method enables us to run any function as a seperate runner by passing it as a argument
    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


#Defining an array to store the youtube links
a = []
#array to store the state of the radio buttons
btnStateArray = []


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #load the style sheet
        apply_stylesheet(app, theme='dark_red.xml')
        stylesheet = app.styleSheet()
        #override style sheet
        with open(resource_path("./custom.css")) as file:
            app.setStyleSheet(stylesheet + file.read().format(**os.environ))
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(690, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(690, 400))
        MainWindow.setMaximumSize(QtCore.QSize(690, 400))
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Triangular)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks | QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        self.convertBtn = QtWidgets.QPushButton(self.centralwidget)
        self.convertBtn.setGeometry(QtCore.QRect(300, 320, 101, 51))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.convertBtn.setProperty('class', 'inverted')
        self.convertBtn.setFont(font)
        self.convertBtn.setObjectName("convertBtn")
        self.convertBtn.clicked.connect(self.initialize)


        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setGeometry(QtCore.QRect(311, 80, 90, 27))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.addBtn.setFont(font)
        self.addBtn.setObjectName("addBtn")
        self.addBtn.clicked.connect(self.add)

        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(410, 50, 271, 321))
        self.listWidget.setObjectName("listWidget")

        self.removeButton = QtWidgets.QPushButton(self.centralwidget, clicked=lambda: self.delete_it())
        self.removeButton.setGeometry(QtCore.QRect(311, 230, 90, 23))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        self.removeButton.setFont(font)
        self.removeButton.setObjectName("removeButton")

        self.clearButton = QtWidgets.QPushButton(self.centralwidget, clicked=lambda: self.clear_it())
        self.clearButton.setGeometry(QtCore.QRect(311, 260, 90, 23))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        self.clearButton.setFont(font)
        self.clearButton.setObjectName("clearButton")

        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 290, 70, 83))

        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.rb1 = QtWidgets.QRadioButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.rb1.setFont(font)
        self.rb1.setObjectName("rb1")
        self.verticalLayout.addWidget(self.rb1)
        self.rb1.toggled.connect(lambda: self.btnstate(self.rb1))
        self.rb2 = QtWidgets.QRadioButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.rb2.setFont(font)
        self.rb2.setObjectName("rb2")
        self.verticalLayout.addWidget(self.rb2)
        self.rb2.toggled.connect(lambda: self.btnstate(self.rb2))
        self.rb3 = QtWidgets.QRadioButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.rb3.setFont(font)
        self.rb3.setObjectName("rb3")
        self.verticalLayout.addWidget(self.rb3)
        self.rb3.toggled.connect(lambda: self.btnstate(self.rb3))
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 60, 195, 60))
        self.label.setObjectName("label")
        #####################################################################
        self.clearPath = QtWidgets.QPushButton(self.centralwidget)
        self.clearPath.setGeometry(QtCore.QRect(311, 160, 90, 27))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.clearPath.setFont(font)
        self.clearPath.setObjectName("clearPath")
        self.clearPath.clicked.connect(self.clearPathButton)
        #####################################################################
        #Open download Folder
        self.openDownload = QtWidgets.QPushButton(self.centralwidget)
        self.openDownload.setGeometry(QtCore.QRect(150, 320, 141, 51))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(8)
        self.openDownload.setFont(font)
        self.openDownload.setAcceptDrops(False)
        self.openDownload.setObjectName("pushButton")
        self.openDownload.clicked.connect(self.openDownloadButton)
        self.changePathBtn = QtWidgets.QPushButton(self.centralwidget)
        self.changePathBtn.setGeometry(QtCore.QRect(20, 160, 151, 27))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.changePathBtn.setFont(font)
        self.changePathBtn.setObjectName("changePathBtn")
        self.changePathBtn.clicked.connect(self.fileBrowser)
        self.pathLabel = QtWidgets.QLabel(self.centralwidget)
        self.pathLabel.setGeometry(QtCore.QRect(20, 110, 351, 19))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")
        self.ytLinkLabel = QtWidgets.QLabel(self.centralwidget)
        self.ytLinkLabel.setGeometry(QtCore.QRect(20, 14, 291, 41))
        font = QtGui.QFont()
        font.setFamily("LEMON MILK Medium")
        font.setPointSize(10)
        self.ytLinkLabel.setFont(font)
        self.ytLinkLabel.setObjectName("ytLinkLabel")
        self.ytPathInput = QtWidgets.QLineEdit(self.centralwidget)
        self.ytPathInput.setGeometry(QtCore.QRect(20, 130, 380, 20))
        self.ytPathInput.setObjectName("ytPathInput")
        self.ytLinkInput = QtWidgets.QLineEdit(self.centralwidget)
        self.ytLinkInput.setGeometry(QtCore.QRect(20, 50, 380, 20))
        self.ytLinkInput.setObjectName("ytLinkInput")
        MainWindow.setCentralWidget(self.centralwidget)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.rb1, self.rb3)
        MainWindow.setTabOrder(self.rb3, self.convertBtn)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YouTube Downloader by FD"))
        self.convertBtn.setText(_translate("MainWindow", "Convert"))
        self.addBtn.setText(_translate("MainWindow", "Add"))
        self.removeButton.setText(_translate("MainWindow", "Remove"))
        self.clearButton.setText(_translate("MainWindow", "Clear"))
        self.rb1.setText(_translate("MainWindow", "MP3"))
        self.rb2.setText(_translate("MainWindow", "MP4"))
        self.rb3.setText(_translate("MainWindow", "wav"))
        self.label.setText(_translate("MainWindow", "Playlist format: \".com/playlist?list\""))
        self.clearPath.setText(_translate("MainWindow", "clear"))
        self.openDownload.setText(_translate("MainWindow", "Open Download\n folder"))
        self.changePathBtn.setText(_translate("MainWindow", "Select Folder..."))
        self.pathLabel.setText(_translate("MainWindow", "Path"))
        self.ytLinkLabel.setText(_translate("MainWindow", "Video or Playlist Link"))

    #check which button is pressed. the names of the button are also the formats so i save them as a string in an array
    def btnstate(self, b):
        if b.isChecked():
            conFormat = b.text()
            conFormat = conFormat.lower()
            print(conFormat)
            global btnStateArray
            btnStateArray = conFormat
    #main function for handling downloads, this functions runs inside the worker class as a seperate thread.
    #fname contains the path from the input box
    #first we check if the array containing the links is empty, if its empty the user is prompted with a pop up window
    #if its filled we match case the button state array we have 4 cases: mp3, mp4, wav and empty
    # case 1-3 download and convert accordingly
    #case 4 handles no button pressed and prompts the user with a pop up box
    #upon completion of case 1-3 success function is called to let the user know the download is completed
    def convert(self):
        #check button state
        fname = self.ytPathInput.text()
        print(btnStateArray)
        if a == []:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Add Music")
            msg.setText("Please enter a link and press \"add\"")
            x = msg.exec_()
        else:
            match btnStateArray:

                case "mp3":
                    for i in a:
                        print(i)
                        format = btnStateArray
                        os.system(f"yt-dlp.exe -i -f ba -x --audio-format {format} {i} -o \"{fname}\%(title)s.%(ext)s\"")
                    self.success()
                case "mp4":
                    for i in a:
                        print(i)
                        format = btnStateArray
                        os.system(f"yt-dlp.exe -i -f ba -x --audio-format {format} {i} -o \"{fname}\%(title)s.%(ext)s\"")
                    self.success()
                case "wav":
                    for i in a:
                        print(i)
                        format = btnStateArray
                        os.system(f"yt-dlp.exe -i -f ba -x --audio-format {format} {i} -o \"{fname}\%(title)s.%(ext)s\"")
                    self.success()
                case []:
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowTitle("select format")
                    msg.setText("please select a format")
                    x = msg.exec_()
    #called when the downloads are done
    def success(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Download complete")
        msg.setText("Thx for using my downloader")
        x = msg.exec_()

    #Future Feature
    #warns if list contains a playlist
    '''def warn(self):
        ytLink = self.ytLinkInput.text()
        if "playlist" in ytLink:
            p = pytube.Playlist(ytLink)
            return p.title
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Contains Playlist")
        msg.setText("List contains 1 or more Playlists")
        x = msg.exec_()'''
    #called during add. this functions runs in the worker class
    #it takes the youtube link from the link input und checks if it contains "playlist" only playlists contain this specific string
    #it returns the title of the playlist as resolving every title in the playlist would take too long
    #if its not a playlist it resolves the name of the video with the pytube module
    #returned in newtitle
    #the data which is passed back is returned with worker.signals.result.connect(self.addToList) as the function is running inside the worker thread
    def playlistCheck(self):
        ytLink = self.ytLinkInput.text()
        if "playlist" in ytLink:
            p = pytube.Playlist(ytLink)
            return p.title
        elif ytLink == "":
            pass
        else:
            title = pytube.YouTube(ytLink)
            newtitle = title.streams[0].title
            print(title.streams[0].title)
            return newtitle
    #opens the fileDialog and saves the selected directory in the path input
    def fileBrowser(self):
        file = QFileDialog.getExistingDirectory()
        self.ytPathInput.setText(file)
    #data from playlistcheck is passed here
    #first the link itself from linkInput is stored in ytLink and then appended to the link array a
    #the payload from playlistcheck is then passed to the list widget on the right side
    def addToList(self, s):
        #ytLinkInput contains the youtube link
        ytLink = self.ytLinkInput.text()
        if ytLink == "":
            pass
        else:
            #append array with the provided link
            a.append(ytLink)
            #print the array
            print(a)
            item = s
            self.listWidget.addItem(item)
            self.ytLinkInput.setText("")
    """def progress(self, n):
        print("%d%% done" % n)"""
    #deletes current selected row in the widget on click of clear button
    def delete_it(self):
        clicked = self.listWidget.currentRow()
        if clicked == -1:
            pass

        else:
            self.listWidget.takeItem(clicked)
            print(clicked)
            a.pop(clicked)
            print(a)
        print("success")

    #clears all entries from the list widget
    def clear_it(self):
        self.listWidget.clear()
        a.clear()
        print(a)
    #on click of add it runs the playlistcheck in the worker thread and passes the data to addToList
    def add(self):
        worker = Worker(self.playlistCheck)
        worker.signals.result.connect(self.addToList)
        #worker.signals.finished.connect(self.thread_complete)
        #worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)
    #on click of convert is starts the convert function inside the worker thread
    def initialize(self):
        worker = Worker(self.convert)
        self.threadpool.start(worker)
    #simply clears the path input
    def clearPathButton(self):
        self.ytPathInput.clear()

    #opens the current download folder
    def openDownloadButton(self):
        directory = self.ytPathInput.text()
        try:
            os.startfile(directory)
        except:
            print("no path input or wrong path")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
