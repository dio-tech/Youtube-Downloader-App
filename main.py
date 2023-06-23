from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import os, time, sys, sqlite3, shutil
from ppadb.client import Client as AdbClient
from pytube import Search
import math

from spotify import Spotify
from youtube import Youtube

conn = sqlite3.connect("D:\Vs_Code\Youtube_Downloader_App\database.db")
c = conn.cursor()


def delete_folder_videos():
    os.chdir("D:\Vs_Code\Youtube_Downloader_App")
    shutil.rmtree("Video Download")


def delete_db():
    conn.execute("DELETE FROM status_text")
    conn.execute("DELETE FROM chosen_id")
    conn.execute("DELETE FROM users where add_user = True")
    conn.commit()


class MainWindow(QtWidgets.QWidget):
    singleton: "MainWindow" = None

    def __init__(self):
        super().__init__()
        # general setup
        self.win = QMainWindow()
        self.win.setWindowTitle("Youtube Downloader")
        self.win.setWindowState(QtCore.Qt.WindowMaximized)

        # parameters
        self.text_ratio = 35
        self.enable_progammer_mode = "Para começar é preciso abilitar a depuração USB no telemóvel!!\nPara isso seguir os seguintes passos: Abrir definições > Acerca do telefone > Informação do software > Clicar 7x em Nº de compilação."
        self.enable_USB = "Com isto feito seguir os seguintes passos: Abrir definições > Opções de programador > Depuração USB.\nCertificar que os dispositivos estão ligados à mesma internet!"
        self.check_USB = 'Após estes passos clicar em "Próximo"'
        self.search_file = "Procurar ficheiro de texto com as músicas para descarregar e clicar em 'Avançar'!!"
        self.not_txt = "Ocorreu um erro por favor tentar novamente!!"
        self.is_txt = "Ficheiro escolhido com sucesso!!!"
        self.chooseFrom = "Por onde quer escolher as suas músicas: Playlist do Spotify ou Ficheiro Local!"
        self.items = ['Spotify', 'Ficheiro Local']
        self.choose_spotify_playlist = "Escolher uma playlist do spotify para descarregar as suas músicas!"

        self.chosen_playlist = ""

        c.execute("SELECT * FROM status_text")
        response = c.fetchall()
        if len(response) > 0:
            self.path_file = response[-1][1]
        else:
            self.path_file = ""

        # Run app
        self.main_win()
        self.win.show()

    @staticmethod
    def restart():
        MainWindow.singleton = MainWindow()

    def create_label(self, text, pos, font="Helvetica", size=12, bold=False, fixed_width=1500):
        label = QtWidgets.QLabel(self.win)
        label.setText(text)
        label.move(pos[0], pos[1])
        label.setFont(QtGui.QFont(font, size))
        label.setFixedHeight(70)
        label.setFixedWidth(fixed_width)
        if bold:
            label.setStyleSheet("font-weight: bold")

    def create_button(self, text, pos, func, width=100):
        button = QtWidgets.QPushButton(self.win)
        button.setText(text)
        button.move(pos[0], pos[1])
        button.setFixedWidth(width)
        button.clicked.connect(func())
    
    def create_combo_button(self, items, pos):
        self.combo = QtWidgets.QComboBox(self.win)
        for item in items:
            self.combo.addItem(item)
        self.combo.move(pos[0], pos[1])
    
    def create_playlist_combo(self, items, pos):
        self.play_combo = QtWidgets.QComboBox(self.win)
        for item in items:
            self.play_combo.addItem(item)
        self.play_combo.move(pos[0], pos[1])
    
    def create_users_combo(self, items, pos):
        self.user_combo = QtWidgets.QComboBox(self.win)
        for item in items:
            self.user_combo.addItem(item)
        self.user_combo.move(pos[0], pos[1])

    def create_entry(self, text, pos):
        entry = QtWidgets.QLineEdit(self.win)
        entry.setText(text)
        entry.move(pos[0], pos[1])
        entry.setFixedWidth(540)
        entry.setDisabled(True)
    
    def create_entry_returnable(self, text, pos):
        entry = QtWidgets.QLineEdit(self.win)
        entry.setText(text)
        entry.move(pos[0], pos[1])
        entry.setFixedWidth(540)

        return entry

    # button functions
    def check_USB_connection(self):
        # check for devices connected with usb
        os.chdir("C:\platform-tools")
        output = os.popen("adb devices")
        conection = ["", ""]
        #print(output.read())

        conn.execute("SELECT * FROM status_text")
        response = c.fetchall()
        if len(response) > 0:
            first = response[-1][1]
            second = response[-1][2]
            index = response[-1][3]
            choice = response[-1][4]
            playlist = response[-1][5]
        else:
            first = ""
            second = ""
            index = ""
            choice = ""
            playlist = ""

        try:
            conection[1] = (
                output.read()
                .replace("List of devices attached", "")
                .replace("\t", "-")
                .split("-")[1]
            )
        except:
            pass
        query = "INSERT INTO status_text VALUES(?, ?, ?, ?, ?, ?)"

        if conection[1].replace("\n", "") == "device":
            params = ("Conectado com sucesso!!", first, second, str(index), choice, playlist)
        elif not "device" in conection[1] and not "unauthorized" in conection[1]:
            params = (
                "Por favor conectar dispositivo e tentar novamente!!",
                first,
                second,
                str(index),
                choice,
                playlist
            )
        elif "unauthorized" in conection[1]:
            params = (
                "Autorizar depuração USB no telemóvel!!\nÉ recomendado desligar e voltar a ligar a depuração USB!!",
                first,
                second,
                str(index),
                choice,
                playlist
            )

        conn.execute(query, params)
        conn.commit()
        # c.execute("SELECT * FROM status_text")

        self.win.close()
        MainWindow.restart()

    def get_file_path(self):
        browse = QtWidgets.QFileDialog.getOpenFileName(
            self.win,
            "Open File",
            "C:",
            "Text Files (*.txt)",
        )
        c.execute("SELECT * FROM status_text")
        response = c.fetchall()
        query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
        params = (
            response[-1][0],
            browse[0],
            response[-1][2],
            response[-1][3],
            response[-1][4],
            response[-1][5]
        )
        conn.execute(query, params)
        conn.commit()

        self.win.close()
        MainWindow.restart()

    def check_file(self):
        c.execute("SELECT * FROM status_text")
        response = c.fetchall()
        query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
        if not response[-1][1].endswith(".txt"):
            params = (response[-1][0], response[-1][1], response[-1][2], self.not_txt, response[-1][4], response[-1][5])
        else:
            params = (response[-1][0], response[-1][1], response[-1][2], self.is_txt, response[-1][4], response[-1][5])
        conn.execute(query, params)
        conn.commit()

        self.win.close()
        MainWindow.restart()

    def send_files(self, yt, w_album=False, album=''):
        yt.send(w_album, album)

        self.win.close()
        MainWindow.restart()
        delete_folder_videos()
    
    def choose_from(self):
        c.execute("SELECT * FROM status_text")
        response = c.fetchall()
        query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
        params = (response[-1][0], response[-1][1], response[-1][2], response[-1][3], self.items[self.combo.currentIndex()], response[-1][5])
        conn.execute(query, params)
        conn.commit()
        MainWindow.restart()
    
    def get_playlist_id(self):
        c.execute("SELECT * FROM chosen_id")
        ident = c.fetchall()[-1][0]
        c.execute("SELECT * FROM status_text")
        response = c.fetchall()
        query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
        params = (response[-1][0], response[-1][1], response[-1][2], "Playlist escolhida com sucesso!!!", response[-1][4], [playlist['id'] for playlist in Spotify().get_playlist(ident)][self.play_combo.currentIndex()])
        conn.execute(query, params)
        conn.commit()
        MainWindow.restart()
    
    def add_user_boolean(self):
        c.execute("SELECT * FROM users")
        query = "INSERT INTO users VALUES (?, ?)"
        params = ("", "True")
        conn.execute(query, params)
        conn.commit()
        MainWindow.restart()
    
    def add_user_btn(self):
        c.execute("SELECT * FROM users")
        responses = c.fetchall()
        user_exists = False
        user_name_exists = False

        for response in responses:
            if response[0] != "":
                if response[0].split('_')[1] == self.ident.text():
                    user_exists = True
                if response[0].split('_')[0] == self.name.text():
                    user_name_exists = True

        if Spotify().check_user(self.ident.text()) == 200:
            if not user_exists:
                if not user_name_exists:
                    query = "INSERT INTO users VALUES (?, ?)"
                    params = (self.name.text() + '_' + self.ident.text(), "False")
                    conn.execute(query, params)
                    conn.commit()
                else:
                    msg = QMessageBox(self.win)
                    msg.setWindowTitle("ERRO!!")
                    msg.setText("Nome de utilizador já existe")
                    msg.exec_()
            else:
                msg = QMessageBox(self.win)
                msg.setWindowTitle("ERRO!!")
                msg.setText("ID já existe")
                msg.exec_()
        else:
            msg = QMessageBox(self.win)
            msg.setWindowTitle("ERRO!!")
            msg.setText("ID não existe!")
            msg.exec_()
        
        MainWindow.restart()
    
    def user(self):
        c.execute("SELECT * FROM users")
        response = c.fetchall()
        # print(response)

        for i in range(len(response)):
            if self.user_combo.currentText() == response[i][0].split('_')[0]:
                self.chosen_ident = response[i][0].split('_')[1]
        
        c.execute("SELECT * FROM chosen_id")
        query = "INSERT INTO chosen_id VALUES (?)"
        params = (self.chosen_ident,)
        conn.execute(query, params)
        conn.commit()
        MainWindow.restart()

    # end of button functions

    def add_user(self):
        c.execute("SELECT * FROM users")
        response = c.fetchall()

        if len(response) > 0:
            if response[-1][1] == "True":
                self.create_label("Nome do utilizador: ", (790, 325))
                self.name = self.create_entry_returnable("", (980, 350))
                self.create_label("ID do utilizador: ", (790, 375))
                self.ident = self.create_entry_returnable("", (980, 390))
                self.create_button("ADICIONAR", (1550, 390), lambda: self.add_user_btn)

    def choose_user(self):
        c.execute("SELECT * FROM users")
        response = c.fetchall()

        self.create_label("Escolher utilizador: ", (270, 325))
        if len([name[0].split('_')[0] for name in response if name[0] != ""]) == 0:
            self.create_users_combo(['None'], (450, 350))
        else:
            self.create_users_combo([name[0].split('_')[0] for name in response if name[0] != ""], (450, 350))
            self.create_button('Escolher utilizador', (450, 400), lambda: self.user, width=150)
        self.create_label("OU", (580, 325))
        self.create_button("Adicionar utilizador", (620, 350), lambda: self.add_user_boolean, width=150)
        self.add_user()
        self.acceptable_for_spotify()
    
    def acceptable_for_spotify(self):
        c.execute("SELECT * FROM users")
        user_response = c.fetchall()
        c.execute("SELECT * FROM chosen_id")
        id_response = c.fetchall()
        if len([name[0].split('_')[0] for name in user_response if name[0] != ""]) > 0:
            if len(id_response) > 0:
                if len([playlist['name'] for playlist in Spotify().get_playlist(id_response[-1][0])]) > 0:
                    # add user info
                    self.create_label(self.choose_spotify_playlist, (50, 420))
                    self.create_playlist_combo([playlist['name'] for playlist in Spotify().get_playlist(id_response[-1][0])], (50, 470))
                    self.create_button("Escolher Playlist", (50, 510), lambda: self.get_playlist_id)
                else:
                    self.create_label("Utilizador não tem playlists", (50, 420))

    def local_file(self):
        self.create_label(self.search_file, (50, 410))
        self.create_button("Browse", (600, 470), lambda: self.get_file_path)
        self.create_entry(self.path_file, (50, 470))
        self.create_button("Avançar", (50, 510), lambda: self.check_file)
    
    def spotify_playlist(self):
        self.choose_user()

    def main_win(self):
        videos = []

        self.create_label(self.enable_progammer_mode, (50, 50))
        self.create_label(self.enable_USB, (50, 95))
        self.create_label(self.check_USB, (50, 140))

        self.create_button("Próximo", (50, 195), lambda: self.check_USB_connection)

        # get status usb
        c.execute("SELECT * from status_text")
        usb_status = c.fetchall()
        if len(usb_status) > 0:
            self.create_label(usb_status[len(usb_status) - 1][0], (50, 240), bold=True)

            if usb_status[len(usb_status) - 1][0] == "Conectado com sucesso!!":
                self.create_label(self.chooseFrom, (50, 290))
                self.create_combo_button(self.items, (50, 350))
                self.create_button('Escolher', (50, 400), lambda: self.choose_from)

                c.execute("SELECT * FROM status_text")
                response = c.fetchall()

                if response[-1][4] != "":
                    if response[-1][4] == 'Ficheiro Local':
                        self.local_file()
                        if response[-1][3] != "":
                            self.create_label(response[-1][3], (50, 535), bold=True)
                            if response[-1][3].endswith("!!!"):
                                yt = Youtube(response[-1][1])
                                yt.videos_to_add = yt.go_through_file()

                                for index, video in enumerate(yt.videos_to_add):
                                    videos.append(video)

                                if len(yt.go_through_file()) > 0:
                                    sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)

                                    for i in range(math.ceil(len(videos)/9)):
                                        start_ratio = 0
                                        for j in range(9):
                                            if j + (9*i) < len(videos):
                                                fixed_width_ = (sizeObject.width() - 30*4 - 50)//5
                                                self.create_label(videos[j + (9*i)].title, (50 + (fixed_width_ + 30)*i , 560 + self.text_ratio*start_ratio), fixed_width=fixed_width_)
                                                start_ratio += 1
                                
                                    if index > 9:
                                        index = 9

                                    # download button
                                    btn = QtWidgets.QPushButton(self.win)
                                    btn.setText("Descarregar")
                                    btn.move(50, 550 + self.text_ratio * (index + 2))
                                    btn.clicked.connect(lambda: self.send_files(yt))

                                    self.create_label(
                                        response[-1][2],
                                        (50, 550 + self.text_ratio * (index + 3)),
                                    )
                                else:
                                    self.create_label('Não existem músicas!!', (50, 540))
                    elif response[-1][4] == 'Spotify':
                        self.spotify_playlist()
                        c.execute("SELECT * FROM status_text")
                        response = c.fetchall()
                        if response[-1][3] != "":
                            self.create_label(response[-1][3], (50, 535), bold=True)
                            if response[-1][3].endswith("!!!"):
                                yt = Youtube(response[-1][1])

                                yt.add_videos(Spotify().get_songs(response[-1][5]))
                                for index, video in enumerate(Spotify().get_songs(response[-1][5])):
                                    videos.append(yt.get_video(video))

                                if len(Spotify().get_songs(response[-1][5])) > 0:
                                    sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)

                                    for i in range(math.ceil(len(videos)/9)):
                                        start_ratio = 0
                                        for j in range(9):
                                            if j + (9*i) < len(videos):
                                                fixed_width_ = (sizeObject.width() - 30*4 - 50)//5
                                                self.create_label(videos[j + (9*i)].title, (50 + (fixed_width_ + 30)*i , 560 + self.text_ratio*start_ratio), fixed_width=fixed_width_)
                                                start_ratio += 1
                                
                                    if index > 9:
                                        index = 9

                                    # download button
                                    btn = QtWidgets.QPushButton(self.win)
                                    btn.setText("Descarregar")
                                    btn.move(50, 550 + self.text_ratio * (index + 2))
                                    btn.clicked.connect(lambda: self.send_files(yt, w_album=True, album=Spotify().get_playlist_name(response[-1][5])))

                                    self.create_label(
                                        response[-1][2],
                                        (50, 550 + self.text_ratio * (index + 3)),
                                    )
                                else:
                                    self.create_label('Não existem músicas!!', (50, 540))


def main():
    app = QApplication([])
    MainWindow.restart()
    sys.exit(app.exec_())


if __name__ == "__main__":
    delete_db()
    main()
