import os
import time
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


# Get user supplied values
#imagePath = sys.argv[1]
cascPath = "haarcascade_frontalface_default.xml"

# Create the haar cascade
faceCascade = cv.CascadeClassifier(cascPath)

video_capture = cv.VideoCapture(0)

d = 0
 
try:
    while True: 
        # Read the image
        ret, frame = video_capture.read()
        #image = cv.imread('image2.jpg')
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        #flags = cv2.CV_HAAR_SCALE_IMAGE
        )
        print("Found faces!",format(len(faces)))

        count1 = format(40 - len(faces))
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


        

# Draw a rectangle around the faces
        for (i,(x, y, w, h)) in enumerate(faces):
           cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
           cv.putText(frame, " #{}".format(i + 1), (x, y - 10),
		cv.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
#image1 = cv.imread(" 	
  
#cv2.imshow("gray image",gray)
   
        filename = "images/file_%d.jpg"%d
        cv.imwrite(filename,frame)
        d+=1

        cv.imshow("Faces found ", frame)
        time.sleep(10)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()

  #key = cv.waitkey(300)&0XFF==27:break
#cv.imwrite('pic.png',frame)
video_capture.release()
cv.waitKey(0)






