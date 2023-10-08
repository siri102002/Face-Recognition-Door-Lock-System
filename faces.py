import pickle,time
import cv2
from gtts import gTTS
import os

face_cascade=cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')  # Reading the stored trained model.

#Loading the label-id relation to get the name of the labels.
with open("label_ids.pickle",'rb') as fr:    
    og_labels=pickle.load(fr)

#labels are of the form {name:id} we want to invert this form to {id:name}
labels={k:v for v,k in og_labels.items()}


print(labels)

def face_recognition():
    flag_face_recognised=False   #to keep track if the user face is recognized
    flag_face_not_recognised=False

    no_of_adjacent_prediction=0
    no_face_detected=0  #to track the number of times the face is detected
    prev_predicted_name=''   #to keep track of the previously predicted face(w.r.t frame)
    cap=cv2.VideoCapture(0)
    count_frames = total_no_face_detected = 0

    while True:
        count_frames+=1
        ret,frame = cap.read()
        # print(ret,frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces=face_cascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5)

        for (x,y,w,h) in faces:

            total_no_face_detected+=1
            no_face_detected+=1

            # print(x,y,w,h)
            roi_gray=gray[y:y+h,x:x+w]  #roi(region of interest)
            # roi_color=frame[y:y+h,x:x+w]
            id,confidence=recognizer.predict(roi_gray)
            print(id,confidence)
            if(confidence>50):
                print("PREDICTED : ",labels[id])
                font=cv2.FONT_HERSHEY_SIMPLEX
                name=labels[id]
                clr=(255,255,255);thickness=2
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

            elif(no_face_detected>=30):
                cv2.putText(frame,"Face Not Recognised",(160,460),font,0.8,clr,thickness,cv2.LINE_AA)
                flag_face_not_recognised=True
                no_of_adjacent_prediction=0
                no_face_detected=0

            cv2.rectangle(frame,(x,y),(end_coord_x,end_coord_y),(0,0,0),2)  #Drawing the rectangle on the frame

        cv2.imshow('Face Recognition',frame)

        if(flag_face_recognised):    #if face is recognized then open the door
            #speak("Welcome "+name.replace('_',' ')+", unlocking door. The door will remain open for the next 5 seconds")
            tts = gTTS("Welcome "+name.replace('_',' ')+", unlocking door. The door will remain open for the next 50 seconds")
            tts.save('hello.mp3')

# Play the MP3 file using the default media player
            os.system('open hello.mp3')
            print("DOOR is OPEN")
            #arduino.write(bytes('o', 'utf-8'))  #Output the given byte string over the serial port.
            
            time.sleep(50)
            #speak("Closing door")
            tts = gTTS("Closing door")
            tts.save('hello1.mp3')

# Play the MP3 file using the default media player
            os.system('open hello1.mp3')
            print("DOOR is OPEN")
            #arduino.write(bytes('c', 'utf-8'))  #Output the given byte string over the serial port.
            print("DOOR is CLOSED")
            flag_face_recognised=False

        if(flag_face_not_recognised):
            #speak("Face not recognised. The door will remain closed")    
            time.sleep(2)
            flag_face_not_recognised=False


        #k=cv2.waitKey(20)     #the key is recieved and converted into ascii value
        #if k==113:  #compairing with the ordinal/ascii value of 'q'
            #break

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    print("No. of frames : ",count_frames," |   No. of times face detected : ",total_no_face_detected)
    cap.release()
    cv2.destroyAllWindows()



if(__name__=="__main__"):
    face_recognition()    