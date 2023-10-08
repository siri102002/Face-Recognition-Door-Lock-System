import cv2
import numpy as np 
from pyzbar.pyzbar import decode   
import pickle,time
import serial  #for serial communication with arduino
from gtts import gTTS
import os

from secret_key import key,registered_users

#Establish connection with arduino
arduino = serial.Serial(port='/dev/cu.usbmodem142401', baudrate=9600)
print("Serial connection established")
print("show the qr code")
#Specify the recognizers
face_cascade=cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')  # Reading the stored trained model.

#Loading the label-id relation to get the name of the labels.
with open("label_ids.pickle",'rb') as fr:    
    og_labels=pickle.load(fr)

#labels are of the form {name:id} we want to invert this form to {id:name}
labels={k:v for v,k in og_labels.items()}

flag=True  # to switch between face recognition and qr code decoding

MAX_TRY=2
tries=0  #for invalid face recognition
flag_face_recognised=False   #to keep track if the user face is recognized
flag_face_not_recognised=False

no_of_adjacent_prediction=0
no_face_detected=0  #to track the number of times the face is detected
prev_predicted_name=''   #to keep track of the previously predicted face(w.r.t frame)
count_frames = total_no_face_detected = 0

time_out_no_of_frames_after_qrcode=0

font=cv2.FONT_HERSHEY_SIMPLEX
clr=(255,255,255)
cap=cv2.VideoCapture(0)
while(True):
    cap=cv2.VideoCapture(0)
    ret,frame = cap.read()

    if(flag):
        for i in decode(frame):
            decoded_data=i.data.decode("utf-8")   #converts bytes to string value
            print(decoded_data)   

            #Drawing polygon on frame (tilts w.r.t orientation)
            pts=np.array([i.polygon],np.int32)

            pts=pts.reshape((-1,1,2))  
            cv2.polylines(frame,[pts],True,(0,0,255),2)
            # print(pts)
        
            #Display text
            rect_pts=i.rect #using rect point as origin for text as we don't want the text to tilt with the qrcode
            fontScale=0.8
            thickness=1
            # cv2.putText(frame,decoded_data,(rect_pts[0],rect_pts[1]),cv2.FONT_HERSHEY_SIMPLEX,fontScale,(255,0,0),thickness)
            # print(rect_pts)
  
            if(decoded_data.lower()=="9bad50377b9f24d5f3e420005f8872a06c47b387e58ed0b5b162e0b0b1789778"):   #Check private key
                flag=False
                tries=0
                print("Valid qr code, proceed to face recognition")
                #cv2.waitKey(5)
                time_out_no_of_frames_after_qrcode=0
                cv2.imshow('Face Recognition Cam',frame)
                
            else:
                print("INVALID QR CODE")

    else:
        count_frames+=1
        time_out_no_of_frames_after_qrcode+=1


        # print(ret,frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces=face_cascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5)

        # print("FACES : ",faces)
        # print(type(frame))   #The frames are automatically converted into numpy arrays of pixels.
        for (x,y,w,h) in faces:

            total_no_face_detected+=1
            no_face_detected+=1

            # print(x,y,w,h)
            roi_gray=gray[y:y+h,x:x+w]  #roi(region of interest)
            # roi_color=frame[y:y+h,x:x+w]ik

            id,confidence=recognizer.predict(roi_gray)
            print(confidence)
            print("PREDICTED : ",labels[id])
            # print(id,confidence,labels[id])
            if(confidence>50 and (labels[id] in registered_users)):
                print("PREDICTED : ",labels[id])
                
                name=labels[id] 
                cv2.putText(frame,name.replace('_',' ').title(),(x,y-5),font,0.8,clr,1,cv2.LINE_AA)

                if(prev_predicted_name==name):
                    no_of_adjacent_prediction+=1
                else:
                    no_of_adjacent_prediction=0

                prev_predicted_name=name        



            # color=(255,0,0) #BGR 0-255
            thickness=1
            end_coord_x=x+w
            end_coord_y=y+h


            if(no_of_adjacent_prediction>15):   #no_of_adjacent_prediction is only updated when the confidence of classification is >80
                cv2.putText(frame,"Welcome home "+name.replace('_',' ').title(),(160,460),font,0.8,clr,thickness,cv2.LINE_AA)  #to print on frame
                flag_face_recognised=True
                no_of_adjacent_prediction=0
                no_face_detected=0

            elif(no_face_detected>=30):   #a face is detected 30 times but not yet recognised or classified, then show user not recognised 
                cv2.putText(frame,"Face Not Recognised",(160,460),font,0.8,clr,thickness,cv2.LINE_AA)
                flag_face_not_recognised=True
                no_of_adjacent_prediction=0
                no_face_detected=0

            cv2.rectangle(frame,(x,y),(end_coord_x,end_coord_y),(0,0,0),2)  #Drawing the rectangle on the frame

        cv2.imshow('Face Recognition Cam',frame)

        if(flag_face_recognised):    #if face is recognized then open the door
            #print("Unlocking door...777")
            arduino.write(bytes('o', 'utf-8'))  
            print("Unlocking door...")
            print("Welcome "+name.replace('_',' ')+", unlocking door. The door will remain open for the next 10 seconds")
            #speak("Welcome "+name.replace('_',' ')+", unlocking door. The door will remain open for the next 10 seconds")

            tts = gTTS("Welcome "+name.replace('_',' ')+", unlocking door. The door will remain open for the next 5 seconds")
            tts.save('hello2.mp3')

            # Play the MP3 file using the default media player
            os.system('open hello2.mp3')
            print("DOOR is OPEN")
           
            # code to keep the door open for 5 seconds
     
            time.sleep(100)
            print("Closing door")
            tts = gTTS("Closing door")
            tts.save('hello3.mp3')
            os.system('open hello3.mp3')
            arduino.write(bytes('c', 'utf-8'))  #Output the given byte string over the serial port.
            print("DOOR is CLOSED")
            flag_face_recognised=False
            flag=True         #to start from qrcode

        if(flag_face_not_recognised):   
            print("Face not recognised. The door will remain closed") 
            tts = gTTS("Face not recognised. The door will remain closed")
            tts.save('hello4.mp3')
            os.system('open hello4.mp3')
            time.sleep(2)
            flag_face_not_recognised=False
            tries+=1
            if(tries>=MAX_TRY):
                print("User authentication failed as face is not recognised")
                tts = gTTS("User authentication failed as face is not recognised")
                tts.save('hello5.mp3')
                os.system('open hello5.mp3')
                flag=True       #to start from qrcode
                tries=0

        if(time_out_no_of_frames_after_qrcode>=400):
            print("User authentication failed due to time out")
            tts = gTTS("User authentication failed due to time out")
            tts.save('hello6.mp3')
            os.system('open hello6.mp3')
            flag=True     #to start from qrcode

    cv2.waitKey(1)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

print("No. of frames : ",count_frames," |   No. of times face detected : ",total_no_face_detected)
cap.release()
cv2.destroyAllWindows()