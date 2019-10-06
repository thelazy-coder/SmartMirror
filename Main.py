import cv2
import csv
import os
import time
import json
import locale
import requests
import threading
import traceback
import multiprocessing
import matplotlib
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk
from contextlib import contextmanager
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gtts import gTTS
from pygame import mixer
import speech_recognition as sr
import subprocess
import time
import sys

loginpath = "data/loginstatus.csv"

matplotlib.use("TkAgg")
style.use("dark_background")
x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,35,36,37,38,39,40,41,42,43,45,46,47,48,49,50]
y = [0,0,0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


email = ''
gpsApi = ''
bioApi = ''
api = "http://68.183.88.242/"

xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 14

bioParsed= None

LOCALE_LOCK = threading.Lock()

map_api="AIzaSyCpqHGLPWICwabnoIg5_78gpsks6o8TSu4"
map_resolution="250x450"
map_type="roadmap"
zoom=14
latitude = None
longitude = None

ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 24 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'in'
weather_api_token = 'd068b507a435bde561f3ad32949453c6' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'si' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values


@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

class Clock(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M:%S') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)

class Weather(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    def get_weather(self):
        try:
            location2 = ""
            weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)
               
            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)
                    
                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather."%e)

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

class HeartRate(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        self.hrt = ''
        self.heartrate_label = Label(self, text=self.hrt, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.heartrate_label.pack(side=TOP)
        self.getHrt()
        
    def getHrt(self):
        bioResponse = requests.post(url=api+bioApi).text
        global bioParsed
        bioParsed = json.loads(bioResponse)
        hrt = bioParsed[len(bioParsed)-1]['fields']['hrt']
        heartrate_text = 'Heart Rate: ' + str(hrt)      
        self.hrt = heartrate_text
        self.heartrate_label.config(text = heartrate_text)
        self.heartrate_label.after(200, self.getHrt)
        
class HeartRateChart(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        f = Figure(figsize=(6,5), dpi=80)
        self.graph = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.heartratechart_label = Label(self, text='', font=('Helvetica', small_text_size), fg="white", bg="black")
        self.heartratechart_label.pack(side=TOP)
        self.canvas.get_tk_widget().pack(side=RIGHT, fill=BOTH, expand=YES)
        self.getHrtChart()
        
    def getHrtChart(self):
        index=0
        while index < len(bioParsed):
            y.append(int(bioParsed[index]['fields']['hrt']))
            del y[0]
            index+=1
                    
        self.graph.clear()
        self.graph.plot(x,y)       
        self.canvas.draw()        
        self.heartratechart_label.after(200, self.getHrtChart)

class GPS(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        self.getGPS()
        '''     img_response = requests.get("https://maps.googleapis.com/maps/api/staticmap?format=jpg&zoom="+str(zoom)+"&size="+map_resolution+"&key="+map_api+"&maptype="+map_type+"&scale:2&markers=size:mid|color:red|"+str(latitude)+","+str(longitude))
        img1 = ImageTk.PhotoImage(Image.open(BytesIO(img_response.content)))
        self.image_label=Label(self,image=img1)
        self.image_label.image=img1
        self.image_label.pack(side = BOTTOM)      
        '''        
    def getGPS(self):
        gpsResponse = requests.post(url=api+gpsApi).text
        gpsParsed = json.loads(gpsResponse)
        global latitude, longitude
        latitude = gpsParsed[len(gpsParsed)-1]['fields']['latitude']
        longitude = gpsParsed[len(gpsParsed)-1]['fields']['longitude']
        '''     img_response = requests.get("https://maps.googleapis.com/maps/api/staticmap?format=jpg&zoom="+str(zoom)+"&size="+map_resolution+"&key="+map_api+"&maptype="+map_type+"&scale:2&markers=size:mid|color:red|"+str(latitude)+","+str(longitude))
        print("0")
        img = ImageTk.PhotoImage(Image.open(BytesIO(img_response.content)))
        print("1")
        self.image_label.configure(image=img)
        print("2")
        self.image_label.image=img
        print("2end")
        #image_label.after(60000, self.getGPS)  
        '''
class FullscreenWindow2:
    def __init__(self):
        self.tk = Tk()
        self.tk.geometry("1360x768")
        self.tk.configure(background='black')
        self.tk.attributes("-fullscreen", True)
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.centerFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill = BOTH, expand = YES)
        self.centerFrame.pack(side = BOTTOM, fill = BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)        

        #FaceID
        global email
        global bioApi
        global gpsApi
        
        self.faceID = database()
        print(self.faceID)
        email = self.faceID.newemail
        bioApi = "getbioinfo/?email="+email
        gpsApi = "getgpsinfo/?email="+email

        #location
        self.gps = GPS(self.bottomFrame)
        self.gps.pack(side=LEFT, anchor=NW, padx=50, pady=100)
        # weather        
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=25, pady=0)
        
        #heartrate
        self.heartrate = HeartRate(self.bottomFrame)
        self.heartrate.pack(side = TOP, anchor=SE, padx=50, pady=50)
        
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=25, pady=25)     

        #heartrate chart
        self.heartrate_chart = HeartRateChart(self.bottomFrame)
        self.heartrate_chart.pack(side = TOP, anchor=SE, padx=50, pady=100)

        #Voice Asst Thread
        self.t1 = threading.Thread(target=VoiceAssistant().runVoiceCommand)        
        self.t1.deamon=True
        self.t1.start()
        
        #self.tk.after(20000,self.killtk)


        # BLANK SPACE
        # self.blankspace1 = Frame(self.topFrame)
        # self.blankspace1.pack(side=LEFT, anchor=N, padx=125, pady=125)
    def changet1status(self):
        self.killtk
    
    def killtk(self):
        print("kill1")
        print("0")
        self.t1.deamon=True
        print("1")
        self.t1.join()  
        print("2")
        self.tk.destroy()
        print("3")
        sys.exit()
              
        
        print("kill2")

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  #Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)

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

    def myCommand(self):
        self.r=sr.Recognizer()
        with sr.Microphone() as source:
            print('Listening ')
            self.r.pause_threshold = 1
            self.r.adjust_for_ambient_noise(source, duration = 1)
            self.audio = self.r.listen(source)
            
        try:
            self.command = self.r.recognize_google(self.audio)        
              
        except sr.UnknownValueError:
            self.assistant(self.myCommand())
            
        except Exception as e:
            print(e)            
            
        else:
            print('You said: '+ self.command + '\n')
            return self.command

    def assistant(self, command):
        try:
            if 'what\'s up' in self.command:
                self.talkToMe('Nothing')
                
            elif 'hello' in self.command:
                self.talkToMe('Hello, How are you')
                
            elif ('fine' or 'good') in self.command:
                self.talkToMe('What would you like to do?')
                
            elif 'music' in self.command:
                self.talkToMe('Playing some music for you')
                mixer.init()
                mixer.music.load("/home/pi/Desktop/SmartMirror/Music/Linkin Park - In The End (Mellen Gi & Tommee Profitt Remix).mp3")
                mixer.music.play()
                while mixer.music.get_busy() == True:
                    continue
                 
            elif ('photos' or 'pictures') in self.command:
                self.talkToMe('Starting Slideshow')
                subprocess.getstatusoutput('feh /home/pi/Desktop/SmartMirror/Pics/*.jpeg -D 2 -Y -Z -x -F --on-last-slide quit')
                
            elif 'show status' in self.command:
                self.talkToMe('Your Vital signs are: ')
            elif (('light' or 'lights' or 'switch') and 'on') in self.command:
                counter=0
                while counter == 0:
                    data =  requests.get("https://api.thingspeak.com/update?api_key=7K4PERKZXSD3C416&field1=1")
                    if data.text != "0":
                        counter=1
                    print(data.text)            
                
                self.talkToMe('Lights are turned ON')
                
            elif (('light' or 'lights' or 'switch') and 'off') in self.command:
                counter=0
                while counter == 0:
                    data =  requests.get("https://api.thingspeak.com/update?api_key=7K4PERKZXSD3C416&field1=0")
                    if data.text != "0":
                        counter=1
                    print(data.text)
                self.talkToMe('Lights are turned OFF')
            self.command=""
            command=""               
                
            
        except Exception as e:
            print(e)
                       
    def runVoiceCommand(self):
        while True:
            self.assistant(self.myCommand())

class database:

    def __init__(self):
        self.newemail=""
        self.readData()
        
    def readData(self):
        with open (loginpath,'r') as f:
            reader=list(csv.reader(f, delimiter=','))
            print(reader)
            self.newemail = reader[0][1]


if __name__ == '__main__':
    FullscreenWindow2().tk.mainloop
