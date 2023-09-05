# USAGE
# python3 pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os
import sys
import paho.mqtt.client as mqtt
import json
import cv2 as cv

THINGSBOARD_HOST = '172.16.51.101'
ACCESS_TOKEN = 'soismanipal'

# Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
INTERVAL=2

#count = {'seats_availabe': 0}
sensor_data = {'seat': 0}
next_reading = time.time() 

client = mqtt.Client()

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

#sending mail
fromaddr = "ruksardevadi@gmail.com"
toaddr = "ruksardevadi@gmail.com"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Criminal Captured"

body = "Hello , Please check the image"
msg.attach(MIMEText(body, 'plain'))

count = 0



# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
video_capture = cv2.VideoCapture(0)

d = 0
try:
  while True:
       
# loop over frames from the video file stream
        ret, frame = video_capture.read()
        # convert the input frame from (1) BGR to grayscale (for face
	# detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                minNeighbors=5, minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)
        print("Found faces!",format(len(rects)))
        count1 = format(40 - len(rects))
        #count2 = 40 - count1
        #print("Count: ",format(count))
        #count['seats_available'] = 10
        sensor_data['seat'] = count1
        
        # Sending humidity and temperature data to ThingsBoard
        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data))

        next_reading += INTERVAL
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
 
	# OpenCV returns bounding box coordinates in (x, y, w, h) order
	# but we need them in (top, right, bottom, left) order, so we
	# need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

	# loop over the facial embeddings
        for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
                matches = face_recognition.compare_faces(data["encodings"],
			encoding)
                name = "Unknown"

		# check to see if we have found a match
                if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
                        for i in matchedIdxs:
                                name = data["names"][i]
                                counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
                        name = max(counts, key=counts.get)
		
		# update the list of names
                names.append(name)
                print(name)

        
        for i in names:
                if i == 'ruksar':
                        count = count + 1
                        if count >= 1 :
                            cv2.imwrite('image.jpg',frame)
                            fp=open('image.jpg','rb')
                            msgImg=MIMEImage(fp.read())
                            fp.close()

                            msg.attach(msgImg)
                            print('Mail composed')

                            server = smtplib.SMTP('smtp.gmail.com', 587)
                            server.starttls()
                            server.login(fromaddr, "raskur@7865")
                            text = msg.as_string()
                            server.sendmail(fromaddr, toaddr, text)
                            server.quit()
                            print('Mail Sent')
                            print ("\n")
                            count = 0
			

	# loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)

	# display the image to our screen
        filename = "images/file_%d.jpg"%d
        cv2.imwrite(filename,frame)
        d+=1
        
        #cv2.imshow("Frame", frame)
        time.sleep(10.0)
        key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
        if key == ord("q"):
               break

	# update the FPS counter
        #fps.update()
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()

        

# stop the timer and display FPS information
#fps.stop()
#print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
#print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()



