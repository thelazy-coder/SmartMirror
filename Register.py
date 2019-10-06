import os
import csv
import cv2
import sys
import PIL.Image
import numpy as np
import subprocess
from tkinter import *
from PIL import Image, ImageTk


path = 'datasets'
dbpath = "data/db.csv"

window=Tk()
window.title("Smart Mirror")
window.geometry("600x600")
window.configure(background = 'black')

labelX=25
textfieldX=130
#Name Input
nameLabel = Label(window, text="Enter Name", fg='white', bg='black',font=('adobe_pi_std', 12))
nameLabel.place(x=labelX,y=50)
nameTextfield = Entry(window, width=20, bg='black', fg="white", font=('adobe_pi_std', 10))
nameTextfield.place(x=textfieldX,y=50)

#Mail Input
emailLabel = Label(window, text="Enter Email", fg='white', bg='black',font=('adobe_pi_std', 12))
emailLabel.place(x=labelX,y=100)
emailTextfield = Entry(window, width=20, bg='black', fg="white", font=('adobe_pi_std', 10))
emailTextfield.place(x=textfieldX,y=100)


#Creating CSV File - Face ID, Email, Name
def writeData():
    try:   
        with open(dbpath,'r') as f:
            reader=csv.reader(f, delimiter=',')
            checkDuplicate=0
            totalrec=0
            for ids in reader:
                e_id=ids[1]
                totalrec+=1;
                if(e_id==emailTextfield.get()):
                    checkDuplicate=1
                else:
                    checkDuplicate=0

            if(checkDuplicate==1):
                msg=Label(window, text='User exists')
                msg.config(bg='black',fg='white', font=('helvetica',10))
                msg.place(x=labelX,y=300)
                window.after(2000,msg.destroy)
                f.close()
            else:
                with open(dbpath, 'a', newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([totalrec+1,emailTextfield.get(),nameTextfield.get()])
                    csvFile.close()
                    
                Dataset(totalrec+1)
                trainer(totalrec+1)
            
    except FileNotFoundError as err:
        f = open(dbpath, 'w')
        writeData()


#DATASET_CREATOR
def Dataset(faceID):

    name=emailTextfield.get()
    faceCascade = cv2.CascadeClassifier('recognizer/haarcascade_frontalface_default.xml')
    video_capture = cv2.VideoCapture(0)	

    entrynumber=0
    while True:
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            entrynumber+=1;
            cv2.imwrite("datasets/User."+str(faceID)+"."+str(entrynumber)+".jpg",gray[y:y+h,x:x+w])
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.waitKey(70)
        cv2.imshow('Video', frame)
        cv2.waitKey(1)
        if(entrynumber>24):
            msg1=Label(window, text='Face Registered Succesfully')
            msg1.config(bg='black',fg='white', font=('adobe_pi_std',15))
            msg1.place(x=labelX, y=300)
            window.after(5000,msg1.destroy)            
            break

            breakvideo_capture.release()
    cv2.destroyAllWindows()

def getImagesWithID(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    faces=[]
    IDs=[]
    for imagePath in imagePaths:
        faceImg=PIL.Image.open(imagePath).convert('L')
        faceNp=np.array(faceImg)
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(faceNp)
        IDs.append(ID)
    return IDs, faces


def trainer(Face_ID):
    recognizer=cv2.face.createLBPHFaceRecognizer();
    Ids,faces=getImagesWithID(path)
    recognizer.train(faces, np.array(Ids))
    recognizer.save('recognizer/trainingData.yml')
    #subprocess.getstatusoutput('rm datasets/*')
    cv2.destroyAllWindows()


#Register Button
register = Button(window, text="Register", command=writeData ,fg="white"  ,bg="black"  ,width=20  ,height=3,font=('adobe_pi_std', 15))
register.place(x=labelX+50, y=150)
