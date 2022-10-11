import traceback
import sys
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QApplication
import os
import subprocess
from qt_material import apply_stylesheet
from design import Ui_MainWindow
import getTitle


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


# Worker class keeps long operations from making it impossible to interact with the gui
# fn contains the function that else blocks the event loop
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.fn = fn
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress

    # this method enables us to run any function as a seperate runner by passing it as a argument
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


# Defining an array to store the youtube links
a = []

# array to store the state of the radio buttons
btnStateArray = []


class DownloaderApp(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        fname = "./path.txt"
        if os.path.isfile(fname) == True:
            with open('path.txt') as f:
                global lines
                lines = f.read()
                self.ui.ytPathInput.setText(lines)
        else:
            pass

        apply_stylesheet(app, theme='dark_red.xml')
        stylesheet = app.styleSheet()
        # override style sheet
        with open(resource_path("./custom.css")) as file:
            app.setStyleSheet(stylesheet + file.read().format(**os.environ))

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.ui.convertBtn.clicked.connect(self.initialize)
        self.ui.addBtn.clicked.connect(self.add)
        self.ui.clearPath.clicked.connect(self.clearPathButton)
        self.ui.pushButton.clicked.connect(self.openDownloadButton)
        self.ui.changePathBtn.clicked.connect(self.fileBrowser)
        self.ui.removeButton.clicked.connect(self.delete_it)
        self.ui.clearButton.clicked.connect(self.clear_it)
        self.ui.rb1.toggled.connect(lambda: self.btnstate(self.ui.rb1))
        self.ui.rb2.setDisabled(True) #.connect(lambda: self.btnstate(self.ui.rb2))
        self.ui.rb3.toggled.connect(lambda: self.btnstate(self.ui.rb3))
        self.ui.ytLinkInput.returnPressed.connect(self.add)

    # check which button is pressed. the names of the button are also the formats so i save them as a string in an array
    def btnstate(self, b):
        if b.isChecked():
            con_format = b.text()
            con_format = con_format.lower()
            global btnStateArray
            btnStateArray = con_format

    def emptyButtonState(self):
        msg = QMessageBox()
        msg.setWindowTitle("select format")
        msg.setText("please select a format")
        x = msg.exec_()
        return

    # opens the fileDialog and saves the selected directory in the path input
    def fileBrowser(self):
        file = QFileDialog.getExistingDirectory()
        self.ui.ytPathInput.setText(file)
        fname = "./path.txt"
        os.path.isfile(fname)
        with open('path.txt', 'w') as f:
                f.write(file)

    def progress(self, n):
        print("%d%% done" % n)

    # deletes current selected row in the widget on click of clear button
    def delete_it(self):
        clicked = self.ui.listWidget.currentRow()
        if clicked == -1:
            pass

        else:
            self.ui.listWidget.takeItem(clicked)
            print(clicked)
            a.pop(clicked)

    # clears all entries from the list widget
    def clear_it(self):
        self.ui.listWidget.clear()
        a.clear()

    # simply clears the path input
    def clearPathButton(self):
        self.ui.ytPathInput.clear()

    # opens the current download folder
    def openDownloadButton(self):
        directory = self.ui.ytPathInput.text()
        try:
            os.startfile(directory)
        except:
            print("no path input or wrong path")

    # Future Feature
    # warns if list contains a playlist
    def warn(self):
        if any("playlist" in ab for ab in a):
            msg = QMessageBox()
            msg.setWindowTitle("Playlist detected")
            msg.setText("List contains 1 or more playlists continue?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            x = msg.exec_()
            return x
        else:
            worker = Worker(self.convert)
            self.threadpool.start(worker)

    # called during add. this functions runs in the worker class
    # it takes the youtube link from the link input und checks if it contains "playlist" only playlists contain this specific string
    # it returns the title of the playlist as resolving every title in the playlist would take too long
    # if its not a playlist it resolves the name of the video with the pytube module
    # returned in newtitle
    # the data which is passed back is returned with worker.signals.result.connect(self.addToList) as the function is running inside the worker thread
    def playlistCheck(self, **kwargs):
        ytLink = self.ui.ytLinkInput.text()
        if "playlist" in ytLink:
            title = getTitle.playlist(ytLink)
            return title
        elif ytLink == "":
            pass
        else:
            title = getTitle.singleVideo(ytLink)
            return title

    # data from playlistcheck is passed here
    # first the link itself from linkInput is stored in ytLink and then appended to the link array a
    # the payload from playlistcheck is then passed to the list widget on the right side
    def addToList(self, s):
        # ytLinkInput contains the youtube link
        ytLink = self.ui.ytLinkInput.text()
        if ytLink == "":
            pass
        if ytLink in a:
            self.ui.ytLinkInput.setText("")
            self.ui.ytLinkInput.setText("link already in list")
            pass
        else:
            # append array with the provided link
            a.append(ytLink)
            # print the array
            item = s
            self.ui.listWidget.addItem(item)
            self.ui.ytLinkInput.setText("")

    # on click of add it runs the playlistcheck in the worker thread and passes the data to addToList
    def add(self):
        worker = Worker(self.playlistCheck)
        worker.signals.result.connect(self.addToList)
        self.threadpool.start(worker)


    # on click of convert is starts the convert function inside the worker thread
    def initialize(self):
        if a == []:
            msg = QMessageBox()
            msg.setWindowTitle("Add Music")
            msg.setText("Please enter a link and press \"add\"")
            x = msg.exec_()
        else:
            x = self.warn()
            match x :
                case 1024:
                    worker = Worker(self.convert)
                    self.threadpool.start(worker)
                case 65536:
                    pass

    # main function for handling downloads, this functions runs inside the worker class as a seperate thread.
    # fname contains the path from the input box
    # first we check if the array containing the links is empty, if its empty the user is prompted with a pop up window
    # if its filled we match case the button state array we have 4 cases: mp3, mp4, wav and empty
    # case 1-3 download and convert accordingly
    # case 4 handles no button pressed and prompts the user with a pop up box
    # upon completion of case 1-3 success function is called to let the user know the download is completed
    def convert(self, progress_callback):
        self.ui.progressBar.setValue(0)
        # check button state
        self.ui.progressBar.setStyleSheet("QProgressBar::chunk "
                                          "{"
                                          "background-color: #ff1744;"
                                          "}")
        fname = self.ui.ytPathInput.text()
        match btnStateArray:
            case "mp3":
                cnt = 1
                for i in a:
                    convert_format = btnStateArray
                    subprocess.run(f"yt-dlp.exe -i -f ba -x --audio-format {convert_format} {i} -o \"{fname}\%(title)s.%(ext)s\"", shell=True)
                    value = cnt * 100 / int(len(a))
                    self.ui.progressBar.setValue(int(value))
                    cnt += 1
                    progress_callback.emit(int(value))
                    self.ui.progressBar.setFormat("Loading..." + str(value))
                self.ui.progressBar.setStyleSheet("QProgressBar::chunk "
                                                    "{"
                                                    "background-color: #52e896;"
                                                    "}")
            case "mp4":
                cnt = 1
                for i in a:
                    convert_format = btnStateArray
                    subprocess.run(f"yt-dlp.exe -f 137+140 {i} -o \"{fname}\%(title)s.%%(ext)s", shell=True)
                    value = cnt * 100 / int(len(a))
                    self.ui.progressBar.setValue(int(value))
                    cnt += 1
                    progress_callback.emit(int(value))
                    self.ui.progressBar.setFormat("Loading..." + str(value))
                self.ui.progressBar.setStyleSheet("QProgressBar::chunk "
                                                  "{"
                                                  "background-color: #52e896;"
                                                  "}")
            case "wav":
                cnt = 1
                for i in a:
                    convert_format = btnStateArray
                    subprocess.run(f"yt-dlp.exe -i -f ba -x --audio-format {convert_format} {i} -o \"{fname}\%(title)s.%(ext)s\"", shell=True)
                    value = cnt * 100 / int(len(a))
                    self.ui.progressBar.setValue(int(value))
                    cnt += 1
                    progress_callback.emit(int(value))
                    self.ui.progressBar.setFormat("Loading..." + str(value))
                self.ui.progressBar.setStyleSheet("QProgressBar::chunk "
                                                  "{"
                                                  "background-color: #52e896;"
                                                  "}")
            case []:
                self.emptyButtonState()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    widget = DownloaderApp()
    widget.show()
    sys.exit(app.exec_())
