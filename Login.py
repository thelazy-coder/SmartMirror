import cv2
import csv
import os
import sys
import time
import json
import locale
import requests
import threading
import traceback
import speech_recognition as sr
import Main

from subprocess import call
from tkinter import *
from io import BytesIO
from pygame import mixer
from PIL import Image, ImageTk
from contextlib import contextmanager
from time import strftime
from gtts import gTTS

dbpath = "data/db.csv"
loginpath = "data/loginstatus.csv"


class FullscreenWindow:
    
    def __init__(self):
        self.tk = Tk()
        self.tk.geometry("1360x768")
        self.tk.configure(background='black')
        self.tk.attributes("-fullscreen", True)
        self.Frame = Frame(self.tk, background = 'black')
        self.Frame.pack(anchor='center')

        self.state = True
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        
        self.screensaver = ScreenSaver(self.Frame)
        self.screensaver.pack(anchor = 'center')

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  #Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

class VoiceAssistant:
    
    def __init__(self):
        pass    
        
    def talkToMe(self, audio):
        self.filename='tempaudio/audio.mp3'
        print(audio)
        self.tts = gTTS(text=audio, lang='en')
        self.tts.save(self.filename)
        mixer.init()
        mixer.music.load(self.filename)
        mixer.music.play()    
                
class ScreenSaver(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        self.string = ''
        self.lbl = Label(self, font=('Helvetica', 40), fg="white", bg="black")
        self.lbl.pack()
        self.msg = Label(self, font=('Helvetica', 20), fg="white", bg="black")
        self.msg.pack()
        self.time()
        with open (loginpath,'w') as f2:
            writer = csv.writer(f2)
            writer.writerow([0,"",""])
            f2.close()
        self.after(2000,self.recognize)
        
    def time(self):
        self.string=strftime('%H:%M:%S')
        self.lbl.config(text=self.string)
        self.lbl.after(1000,self.time)

    def recognize(self):
        faceCascade = cv2.CascadeClassifier('recognizer/haarcascade_frontalface_default.xml')
        video_capture = cv2.VideoCapture(0)	

        rec = cv2.face.createLBPHFaceRecognizer()
        rec.load("recognizer/trainingData.yml")
        id=0
        
        loopcheck=True
        
        while loopcheck:
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)

            for (x, y, w, h) in faces:
                id,conf=rec.predict(gray[y:y+h,x:x+w])

                with open(dbpath,'r') as f:
                    reader=csv.reader(f, delimiter=',')

                    for ids in reader:
                        face_id=ids[0]    
                        if (face_id == str(id)):
                            email = ids[1]
                            name = ids[2]

                            with open (loginpath,'w') as f2:
                                writer = csv.writer(f2)
                                writer.writerow([id,email,name])
                                f2.close()

                if(conf<60):
                    
                    print ("Face Matched "+str(id))
                    loopcheck=False
                    VoiceAssistant().talkToMe(audio="Welcome to Smart Mirror "+str(name))
                    Main.FullscreenWindow2().tk.mainloop
        
if __name__ == '__main__':
    FullscreenWindow().tk.mainloop
      
