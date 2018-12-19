from tkinter import *
import os, time, sys, logging, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib as sm
import PIL as pil
from PIL import Image
from PIL import ImageTk




import cv2 as cv, datetime as dt, numpy as np, time as t, smtplib as sm

#from folder.py_interface import Window

class Security_cam(Frame):
    global Frame
    def __init__(self, master = None):
        Frame.__init__(self, master)
        #main frame
        self.master = master

        self.image_0 = None
        self.image_1 = None
        self.image_2 = None
        self.video = cv.VideoCapture(0)
        self.rm_status = None
        self.time_stamp = None
        #my functions
        self.init_window()

    def init_window(self):
        title = "Motion Capture Security Software"
        self.master.title(title)

        self.pack(fill= BOTH, expand = 1)

        #create a button and link it to an event
        name = "MCS2 Security"
        label = Label(self,
        text = name,
        fg = "orange",
        padx = 2,
        font=("Helvetica", 30))

        label.pack()

        #background imageMC
        path = "---"
        photo = PhotoImage(file= path)
        w = Label(master=None, image = photo)
        w.photo = photo
        w.pack()

        #create a label for instructions
        text_instructions = "Please press start to continue:"
        instructions = Label(self,
        text = text_instructions,
        fg = "#383a39",
        padx = 2,
        font = ("Helvetica", 16))

        instructions.pack()

        btnFrame = Frame(self)

        #create a start button
        startButton = Button(btnFrame,
        text = "Start", width=20,
        height = 2,
        fg = "red",
        padx = 2,
        borderwidth = 5,
        font = ("Helvetica", 16),
        command = self.client_initiate)

        #create an exit button
        exitButton = Button(btnFrame,
        text = "Exit", width=20,
        height = 2,
        fg = "red",
        padx = 2,
        borderwidth = 5,
        font = ("Helvetica", 16),
        command = self.client_exit)


        startButton.pack(side = LEFT)
        exitButton.pack(side = LEFT)

        btnFrame.pack(side = BOTTOM)
        #create a menu




    #opencv time
    def client_initiate(self):
        rm_status = ""
        #video = cv.VideoCapture(0)

        # read and store first three images
        image_0 = cv.cvtColor(self.video.read()[1], cv.COLOR_RGB2GRAY)     #also turns the image to grayscale
        image_1 = cv.cvtColor(self.video.read()[1], cv.COLOR_RGB2GRAY)
        image_2 = cv.cvtColor(self.video.read()[1], cv.COLOR_RGB2GRAY)
        time_stamp = dt.datetime.now().strftime("%Ss")

        #self.video = self.detection(image_0, image_1, image_2, time_stamp, rm_status)
        self.detection(image_0, image_1, image_2, time_stamp, rm_status)



    def compare_image(self, image_0, image_1, image_2):
        diff_1 = cv.absdiff(image_2, image_1)
        diff_2 = cv.absdiff(image_1, image_0)
        return cv.bitwise_and(diff_1, diff_2)


    def detection(self, image_0, image_1, image_2, time_stamp, rm_status):
        face_resource = "---"
        face_cascade = cv.CascadeClassifier(face_resource)
        # counter to change rm_status if no movement
        counter = 0
        # counter to create intervals between pictures taken if face is detected
        face_frame_count = 0
        # counter to create intervals between pictures taken if movement and face is detected
        movement_face_frame_count = 0
        # counter to create intervals between pictures taken if movement is detected
        movement_frame_count = 0

        while True:
            global frame
            ret, frame = self.video.read()
            frame = cv.resize(
            frame,
            None,
            fx=0.5,
            fy=0.5,
            interpolation=cv.INTER_AREA)



            #face detection
            face_found = self.face_detection(frame, face_cascade)

            current_time = dt.datetime.now().strftime("%Ss")
            #cv2.putText(frame, text, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

            # first condition checks if only the face is detected
            if face_found:
                rm_status = "Face Detected: Human Found."
                if face_frame_count == 0 or face_frame_count == 50:
                    face_frame_count = 0
                    self.detection_logger(frame)

                face_frame_count += 1
                #print(face_frame_count)
            # second condition checks if face and movement are detected
            elif cv.countNonZero(self.compare_image(image_0, image_1, image_2)) > 350000  and time_stamp != current_time and face_found:
                #read and store image with movement
                rm_status = "Face Detected: Human Found."
                if movement_face_frame_count == 0 or movement_face_frame_count == 50:
                    movement_face_frame_count = 0
                    self.detection_logger(frame)

                movement_face_frame_count += 1
            # third condition checks if only movement is deteted
            elif cv.countNonZero(self.compare_image(image_0, image_1, image_2)) > 350000 and time_stamp != current_time:
                rm_status = "Movement Detected"
                if movement_frame_count == 0 or movement_frame_count == 5:
                    movement_frame_count = 0
                    self.detection_logger(frame)
                movement_frame_count += 1
            # last condition checks if there is no movement at all
            else:
                counter += 1
                if counter >=50:
                    rm_status = ""
                    counter = 0

            time_stamp = dt.datetime.now().strftime("%Ss")

            #read and store incomming image
            image_0 = image_1
            image_1 = image_2
            image_2 = cv.cvtColor(self.video.read()[1], cv.COLOR_BGR2GRAY)

            # update status of security cam on screen
            cv.putText(
            frame,
            "{}".format(rm_status),
            (10, 20),
            cv.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 255),
            2)

            cv.putText(
            frame,
            "{}".format("Live"),
            (560, 20),
            cv.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 255),
            2)
            time = dt.datetime.now().strftime("%Y-%m-%d %Hh:%Mm:%Ss%f")

            cv.putText(
            frame,
            "{}".format(time),
            (10, 344),
            cv.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 255),
            2)


            fr = self.Refresher(frame)
            fr.update()
            cv.imshow("MC Security Cam", frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                self.video.release()
                cv.destroyAllWindows()
                break




    def face_detection(self, frame, face_cascade):

        face_found = False   #---Initially set the flag to be False
        face_collection = face_cascade.detectMultiScale(
            frame,
            scaleFactor = 1.3,
            minNeighbors = 5,
            minSize = (30, 30),
            flags = 0
        )
        for (topLeft, bottomRight, width, height) in face_collection:
            if width > 0 :                 #--- Set the flag True if w>0 (i.e, if face is detected)
                face_found = True
            cv.rectangle(frame,
            (topLeft, bottomRight),
            (topLeft + width, bottomRight + height),
            (255, 0, 0),
            2)
        return face_found

    #logs pictures of motion that is detected
    def detection_logger(self,frame):


        img_moving = self.video.read()[1]
        img_name = dt.datetime.now().strftime("%Y-%m-%d %Hh:%Mm:%Ss%f") + '.jpg'
        string = cv.imwrite(img_name, img_moving)
        self.email_notification(img_name)



    def email_notification(self,img):

        frm = "---"
        to = "---"
        subject = "Something moved! Review the Screenshot"
        msg = MIMEMultipart()

        msg['From'] = frm
        msg['To']= to
        msg['Subject'] = subject
        host = 'smtp.gmail.com'
        port = 587

        message = "Here is your screenshot provided by mc security. \n\n"
        msg.attach(MIMEText(message, 'plain'))

        conn = smtplib.SMTP(host, port)

        img_data = open(img, 'rb').read()
        #body = MIMEText("test")
        #msg.attach(text)
        image = MIMEImage(img_data, name=os.path.basename(img))
        msg.attach(image)
        # And imghdr to find the types of our image
        conn.ehlo()

        conn.starttls()
        conn.login(frm, "---")
        body = msg.as_string()
        conn.sendmail(frm, to, body)
        {}

        conn.quit()

    def client_exit(self):
            sys.exit()

    def Refresher(self, frame):
        vid_Frame = Frame(self)

        img = Image.fromarray(frame)
        #img = img.save('my.png')
        img = ImageTk.PhotoImage(img)
        w = Label(vid_Frame, image = img)
        w.img = img
        w.pack(side = "bottom", padx = 10, pady = 10)
        vid_Frame.pack()
        return vid_Frame



#create a window
root = Tk()

root.geometry("500x400+600+400")
root.resizable(False, False)
cam = Security_cam(root)
root.mainloop()
