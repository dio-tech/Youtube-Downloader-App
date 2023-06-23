import os
import sqlite3
from pytube import Search
from ppadb.client import Client as AdbClient
from spotify import *

conn = sqlite3.connect("D:\Vs_Code\Youtube_Downloader_App\database.db")
c = conn.cursor()


class Youtube:
    def __init__(self, file_path):
        self.file_path = file_path
        self.videos_to_add = []

    def get_video(self, name):
        videos = Search(name)
        # get top video
        video = videos.results[0]
        return video

    def go_through_file(self):
        videos_to_add = []
        file = open(self.file_path, "r")

        for line in file.readlines():
            videos_to_add.append(self.get_video(line))

        return videos_to_add
    
    def add_videos(self, videos):
        for video in videos:
            self.videos_to_add.append(video)

    def download(self):
        c.execute("SELECT * FROM status_text")
        response = c.fetchall()

        if response[-1][4] == "Ficheiro Local":
            videos = self.videos_to_add
        else:
            videos = [self.get_video(song) for song in Spotify().get_songs(response[-1][5])]

        os.chdir("D:\Vs_Code\Youtube_Downloader_App")
        os.mkdir("Video Download")
        os.chdir("D:\Vs_Code\Youtube_Downloader_App\Video Download")

        for video in videos:
            video.streams.filter(only_audio=True).first().download()

    def send(self, with_album=False, album=''):
        self.download()
        client = AdbClient()
        devices = client.devices()

        os.chdir("D:\Vs_Code\Youtube_Downloader_App\Video Download")
        for dirpath, dirname, filename in os.walk(os.getcwd()):
            for file in filename:
                os.rename(file, file.replace(".mp4", ".mp3"))
        if len(devices) == 1:
            for dirpath, dirname, filename in os.walk(os.getcwd()):
                for file in filename:
                    if file.endswith(".mp3"):
                        if with_album:
                            devices[0].push(
                                dirpath + "/" + file,
                                f"/storage/emulated/0/Music/{album}/" + file,
                            )
                        else:
                            devices[0].push(
                                dirpath + "/" + file,
                                "/storage/emulated/0/Music/" + file,
                            )
                        c.execute("SELECT * FROM status_text")
                        response = c.fetchall()
                        query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
                        params = (
                            response[-1][0],
                            response[-1][1],
                            "Ficheiros descarrgeados com sucesso!!\nSe quiser descarregar mais basta repetir o processo!!",
                            response[-1][3],
                            response[-1][4],
                            response[-1][5]
                        )
        elif len(devices) > 1:
            c.execute("SELECT * FROM status_text")
            response = c.fetchall()
            query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                response[-1][0],
                response[-1][1],
                "Por favor manter apenas um dispositivo conectado!!",
                response[-1][3],
                response[-1][4],
                response[-1][5]
            )
        elif len(devices) == 0:
            c.execute("SELECT * FROM status_text")
            response = c.fetchall()
            query = "INSERT INTO status_text VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                response[-1][0],
                response[-1][1],
                "Por favor conectar dispositivo!!",
                response[-1][3],
                response[-1][4],
                response[-1][5]
            )

        conn.execute(query, params)
        conn.commit()