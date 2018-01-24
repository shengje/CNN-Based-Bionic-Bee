from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers.normalization import BatchNormalization
from keras import backend as K
from keras.preprocessing import image
import numpy as np
import time
import cv2
import msvcrt
import os
import csv
import datetime

# dimensions of our images.
img_width, img_height = 250, 140

class_number=6
data_version=3

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

model = Sequential()

model.add(Conv2D(32, (3, 3), input_shape=input_shape))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(128, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(256, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(256, (3, 3)))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(1024))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(class_number))
model.add(Activation('sigmoid'))

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])


if class_number==5:
    class_dict={0:'flower',1:'front',2:'left',3:'right',4:'stop'}
    if data_version==1:  
        model.load_weights('drone_control_5class_indoor_5C1F_V2-1.h5')
    elif data_version==2:
        model.load_weights('drone_control_5class_indoor_5C1F_V2-2.h5')
elif class_number==6:
    class_dict={0:'down',1:'front',2:'left',3:'right',4:'stop',5:'up'}
    if data_version==1:  
        model.load_weights('drone_control_6class_drone_capture_image_5C1F_V1.h5')
    elif data_version==2:
        model.load_weights('drone_control_6class_drone_capture_image_5C1F_V2.h5')
    elif data_version==3:
        model.load_weights('drone_control_6class_drone_capture_image_5C1F_V3.h5')
elif class_number==7:
    class_dict={0:'down',1:'flower',2:'front',3:'left',4:'right',5:'stop',6:'up'}
    if data_version==1:  
        model.load_weights('drone_control_7class_indoor_5C1F_V2-1.h5')
    elif data_version==2:
        model.load_weights('drone_control_7class_indoor_5C1F_V2-2.h5')  

#test_data_dir='data_test'

'''setting image being tested'''

#t = time.time()

###############################################
#test_file_name='test13.jpg'
###############################################

'''predicting images'''
from pymultiwii import MultiWii

j = 1

if __name__ == "__main__":
    pitch=1500
    roll=1500
    rotate=1500
    throttle=1000
    changerate = 10
    i = 0
    cam = 1
    control_signal_log={}
    control_signal_log_timer_start=time.time()
    board = MultiWii("COM4")
    #cap = cv2.VideoCapture(0)
    try:
        print('Press button g to start control')
        print('Press button q to quit ')
        while True:
            #camera show
            #ret, frame = cap.read()
            #cv2.imshow('frame',frame)
            #cv2.imwrite('img{:>05}.png'.format(i), frame)
            CNN = -1
            prestate = 'None'
            if(msvcrt.kbhit()):
                key = msvcrt.getch()
                if  (key.decode() == 'd'):
                    board.disarm()
                    print("Disarmed.")
                elif(key.decode() == 'q'):
                    print('Quit...')
                    break
                elif(key.decode() == 'c'):
                    if(cam == 1):
                        cam = 0
                        print('camera number change to 0')
                    elif(cam == 0):
                        cam = 1
                        print('camera number change to 1')
                elif(key.decode() == 'g'):
                    cap = cv2.VideoCapture(cam)
                    while True:
                        pitch=1500
                        roll=1500
                        rotate=1500
                        t = time.time()
                        #camera show
                        ret, frame = cap.read()
                        cv2.imshow('frame', frame)
                        
                        #press to control 
                        if(msvcrt.kbhit()):
                            key = msvcrt.getch()
                            if(key.decode() == 'a'): #arm
                                board.arm()
                                print("Drone is armed now!")
                            elif(key.decode() == 'd'): #disarm
                                board.disarm()
                                print("Disarmed.")
                            elif(key.decode() == 'r'): #reset
                                pitch = 1500
                                roll = 1500
                                rotate = 1500
                                throttle = 1000
                                CNN = -1
                            elif(key.decode() == 'u'): #left
                                #pitch = 1400
                                roll = 1300
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                #pitch = 1500
                                roll = 1500
                            elif(key.decode() == 'o'): #right
                                #pitch = 1600
                                roll = 1700
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                #pitch = 1500
                                roll = 1500
                            elif(key.decode() == 'j'): #spin left
                                rotate = 1300
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                rotate = 1500
                            elif(key.decode() == 'l'): #spin right
                                rotate = 1700
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                rotate = 1500
                            elif(key.decode() == 'w'): #up
                                throttle = throttle + changerate
                            elif(key.decode() == 's'): #down
                                throttle = throttle - changerate
                            elif(key.decode() == 'i'): #front
                                pitch = 1700
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                pitch = 1500
                            elif(key.decode() == 'k'): #back
                                pitch = 1300
                                data = [roll, pitch, rotate, throttle]
                                board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                print(data)
                                time.sleep(0.1)
                                pitch = 1500
                            elif(key.decode() == 'f'): #快速上升
                                throttle = 1700
                            elif(key.decode() == 'x'): #緩降
                                while throttle > 1400:
                                    throttle = throttle - 1
                                    data = [roll, pitch, rotate, throttle]
                                    board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                                    print(data)
                                    time.sleep(0.005)
                                time.sleep(1)
                                throttle = 1000
                                break
                            elif(key.decode() == 'c'):
                                CNN = -CNN
                                if(CNN == 1):
                                    print('CNN start')
                                    time.sleep(1)
                                elif(CNN == -1):
                                    print('CNN stop')
                                    #time.sleep(1)
                            elif(key.decode() == 'q'):
                                #cap.release()
                                #cv2.destroyAllWindows()
                                print('break the control loop')
                                print('press button g to start or button q to quit...')
                                break
                        #CNN auto control
                        elif(CNN == 1):
                            img = cv2.resize(frame, (140,250), interpolation = cv2.INTER_CUBIC)
                            x = image.img_to_array(img)
                            x=x/255
                            x = np.expand_dims(x, axis=0)

                            images = np.vstack([x])
                            prediction = model.predict(images, batch_size=1)

                            first = 0
                            two = 0
                            for i in range(class_number):
                                #print('%s:%f  '%(class_dict[i],prediction[0][i]),sep='',end='')
                                if (prediction[0][i] > first):
                                    first = prediction[0][i]
                                    top1 = class_dict[i]
                                elif (prediction[0][i] > two):
                                    two = prediction[0][i]
                                    top2 = class_dict[i]
                            print('                 ',top1,':',first)

                            if(top1 == 'front'):
                                if(prestate == 'front2'):
                                    pitch = 1500
                                    prestate = 'front'
                                else:
                                    pitch = 1600
                                    prestate = 'front2'
                            elif(top1 == 'stop'):
                                if(prestate == 'stop2'):
                                    pitch = 1500
                                    prestate = 'stop'
                                else:
                                    pitch = 1450
                                    prestate = 'stop2'
                            elif(top1 == 'up'):
                                if(throttle < 1800):
                                    throttle = throttle + 5
                                    prestate = 'up'
                                else:
                                    throttle = 1800
                                    prestate = 'up'
                            elif(top1 == 'down'):
                                if(throttle > 1600):
                                    throttle = throttle - 5
                                    prestate = 'down'
                                else:
                                    throttle = 1600
                                    prestate = 'down'
                            elif(top1 == 'left'):
                                rotate = 1350
                                prestate = 'left'
                            elif(top1 == 'right'):
                                rotate = 1650
                                prestate = 'right'

                            
                            print('\nruntime: %f s'%(time.time()-t))

                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        #send data to CMD
                        data = [roll, pitch, rotate, throttle]
                        board.sendCMD(8, MultiWii.SET_RAW_RC, data)
                        print(data)

                        if throttle!=1000:
                            control_signal_log["%.2f" % (time.time()-control_signal_log_timer_start)]=data

                     #When everything done, release the capture
                    cap.release()
                    cv2.destroyAllWindows()
            else:
                key = 'n'
    except Exception as error:
        print ("Error on Main: "+str(error))
        
file_name=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

with open('control_signal_log/'+file_name+'.csv', 'w', newline='') as csvfile:
    fieldnames=['time','roll','pitch','rotate','throttle']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for item in control_signal_log:
        writer.writerow({'time':item,'pitch':control_signal_log[item][0],'roll':control_signal_log[item][1],'rotate':control_signal_log[item][2],'throttle':control_signal_log[item][3]})
        

