# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 14:13:52 2017

@author: 蔡永聿
"""

'''
xbox1 controller
pymultiwii
pygame console FPV combined
CNN testing ( navigation + flower detection )
'''

import pygame,time,datetime,csv,cv2
from pymultiwii import MultiWii
#from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers.normalization import BatchNormalization
from keras import backend as K
from keras.preprocessing import image
import numpy as np
import msvcrt


##########################################################################################################
#variables 
class_number=4
class_dict={0:'front',1:'left',2:'right',3:'stop'}
navigation_weight_file_name='drone_control_drone_capture_image_5C1F_EE_2F_4class_v2_small_resolution.h5'
flower_weight_file_name='is_flower_5C1F_V4.h5'
flower_prob_threshold=0.75
auto_takeoff_throttle=1700
##########################################################################################################

# dimensions of our images.
img_width, img_height = 140, 140

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

def buildmodel(class_number,weight_file_name):
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

    model.load_weights(weight_file_name)

    return model

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 50)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 30
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10


class xbox1:
	joystick=0
	joystick_count=0
	numaxes=0
	numbuttons=0
	left=right=up=down=lb=rb=A=B=X=Y=share=menu=xbox=joystick_left=joystick_right=0
	a_joystick_left_x=a_joystick_left_y=a_joystick_right_x=a_joystick_right_y=a_trigger=0
	
	#Initialize the controller when the oject is created
	def __init__(self):
		#Make the stdout buffer as 0,because of bug in Pygame which keeps on printing debug statements
		#http://stackoverflow.com/questions/107705/python-output-buffering
		#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
		
		xbox1.joystick = pygame.joystick.Joystick(0)
		xbox1.joystick.init()
		xbox1.joystick_count = pygame.joystick.get_count()
		xbox1.numaxes = xbox1.joystick.get_numaxes()
		xbox1.numbuttons = xbox1.joystick.get_numbuttons()
        #modified
		#get count of joysticks=1, axes=27, buttons=19 for DualShock 3
	
	#Update the button values
	def update(self):
		button_state=[0]*self.numbuttons
		button_analog=[0]*self.numaxes
		#while loopQuit == False:
		
		#Start suppressing the output on stdout from Pygame
		#devnull = open('/dev/null', 'w')
		#oldstdout_fno = os.dup(sys.stdout.fileno())
		#os.dup2(devnull.fileno(), 1)
		
		#Read analog values
		for i in range(0,self.numaxes):
			button_analog[i] = self.joystick.get_axis(i)	

		self.a_joystick_left_x	=button_analog[0]
		self.a_joystick_left_y	=button_analog[1]
		self.a_joystick_right_y	=button_analog[3]
		self.a_joystick_right_x	=button_analog[4]
		self.a_trigger	        =button_analog[2]

		
		#Read digital values
		for i in range(0,self.numbuttons):
			button_state[i]=self.joystick.get_button(i)
            
		self.A			      =button_state[0]
		self.B	            =button_state[1]
		self.X	            =button_state[2]
		self.Y			      =button_state[3]
		self.lb				   =button_state[4]
		self.rb				   =button_state[5]
		self.share		      =button_state[6]
		self.menu			   =button_state[7]
		self.joystick_left   =button_state[8]
		self.joystick_right  =button_state[9]

		if self.joystick.get_hat(0)[1]==1:
		    self.up				=1
		else:
  		    self.up				=0
              
		if self.joystick.get_hat(0)[0]==1:
		    self.right			=1
		else:
  		    self.right			=0
              
		if self.joystick.get_hat(0)[1]==-1:
		    self.down			=1
		else:
  		    self.down			=0
              
		if self.joystick.get_hat(0)[0]==-1:
		    self.left			=1
		else:
  		    self.left			=0


		#Enable output on stdout
		#os.dup2(oldstdout_fno, 1)	
		#os.close(oldstdout_fno)
		
		#refresh
		pygame.event.get()
		return button_analog

#build models
model1=buildmodel(4,navigation_weight_file_name)

model2=buildmodel(1,flower_weight_file_name)

pygame.init()
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()

# Set the width and height of the screen [width,height]
size = [1300, 600]

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

camera_num = 0

if __name__ == "__main__":
    
    program_run=True

    butterfly = MultiWii("COM4")
    print("Butterfly Connected")
    time.sleep(1)
    controller=xbox1()
    print("Controller Connected")
    time.sleep(1)
    sensitivity=200 #max 500
    print('Default Sensitivity : %d' % sensitivity)
    time.sleep(1)
        
    while program_run:
        controller.update()

        
        screen = pygame.display.set_mode(size)
    
        pygame.display.set_caption("Control Panel")
    
        idle=True
        while idle:
            screen.fill(WHITE)
            textPrint.reset()
            textPrint.print(screen, "Ready to Fly {}".format(" ") )
            textPrint.print(screen, " {}".format(" ") )
            textPrint.print(screen, "press X button to start {}".format(" ") )
            textPrint.print(screen, " {}".format(" ") )
            textPrint.print(screen, "press Share button to quit {}".format(" ") )
            textPrint.print(screen, " {}".format(" ") )
            textPrint.print(screen, "Camera Number(Press A to change) : {}".format(camera_num))

            controller.update()

            if controller.share:
                program_run=False
                idle=False
            elif controller.X:
                idle=False
                #Loop until the user clicks the close button.
                done = False
            elif controller.A:
                camera_num = camera_num * (-1) + 1 

            pygame.display.flip()

            clock.tick(2)

        
        roll=1500
        pitch=1500
        rotate=1500
        throttle=1000
        
        roll_offset=0
        pitch_offset=0
        rotate_offset=0
        
        butterfly.disarm()
        
        console_messege_timer_start=0
        auto_land=False
        auto_pilot=False
        flower_detected=False
        
        control_signal_log={}
        #captured_image_log={}
        predicted_probability_log={}
        top_label_log={}
        log_timer_start=time.time()
        flying_state_log={}
        flower_probability_log={}

        flying_state='prepare' #the mode of flying condition 'prepare' , 'auto_pilot' ,' interrupt'
        prestate='None'
        prestate2 = 'None'
        frontcontrol = True
        flower_prob_counter=0
        
        cap = cv2.VideoCapture(camera_num)
        
        try:
            # -------- Main Program Loop -----------
            while done==False:
                ret, frame = cap.read()

                # EVENT PROCESSING STEP
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        done=True # Flag that we are done so we exit this loop

                idle=False
                # DRAWING STEP
                # First, clear the screen to white. Don't put other drawing commands
                # above this, or they will be erased with this command.
                screen.fill(WHITE)
                textPrint.reset()
                                
                loop_time=time.time()-log_timer_start             
                runtime = time.time()
                
                img = cv2.resize(frame, (140,140), interpolation = cv2.INTER_CUBIC)
                #img = np.swapaxes(frame, 0, 1)
                #img = np.fliplr(img)
                x = image.img_to_array(img)
		x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.swapaxes(frame,0,1)
                frame = pygame.surfarray.make_surface(frame)
                screen.blit(frame, (600,100))
                
                images = np.vstack([x])
                prediction = model1.predict(images, batch_size=1)
                prediction = prediction[0]

                flower_prob = model2.predict(images, batch_size=1)
                flower_prob = flower_prob[0]

                if time.time() - console_messege_timer_start > 2:
                    console_messege=" "
                
                first=0
                two = 0
                for i in range(class_number):
                    if (prediction[i] > first):
                        first = prediction[i]
                        top1 = class_dict[i]
                    elif (prediction[i] > two):
                        two = prediction[i]
                        top2 = class_dict[i]
                
                if flower_prob[0]>flower_prob_threshold and flying_state=="auto_pilot":
                    flower_prob_counter=flower_prob_counter+1
                    if flower_prob_counter>5:
                        auto_land=True
                        console_messege="Flower Detected!!!"
                        flower_prob_counter=0

                else:
                    flower_prob_counter=0

                controller.update()
                
                #button function    
                if controller.B:#arm
                    butterfly.arm()
                    console_messege="Armed."
                    console_messege_timer_start =  time.time()
                elif controller.A:#disarm
                    butterfly.disarm()
                    console_messege="Disarmed."
                    console_messege_timer_start =  time.time()
                elif controller.Y:#stop flying
                    done=True        	
                elif controller.X:#default control signal
                    pitch=1500
                    roll=1500
                    rotate=1500
                    throttle=1000 
                elif controller.rb:#increase sensitivity
                    if sensitivity<500:
                        sensitivity=sensitivity+50
                elif controller.lb:#decrease sensitivity
                    if sensitivity>100:
                        sensitivity=sensitivity-50
                elif controller.up:#directly set throttle to 1700
                    throttle=auto_takeoff_throttle
                    console_messege="Auto Take Off"
                    console_messege_timer_start =  time.time()
                elif controller.down or auto_land==True:#auto land
                    if throttle>1400 and (abs(controller.a_joystick_right_x)<0.1 and abs(controller.a_joystick_right_y)<0.1 and abs(controller.a_trigger)<0.1):
                        auto_land=True
                        throttle = throttle - 3
                    else:
                        auto_land=False
                    if console_messege!="Flower Detected!!!":
                        console_messege="Auto Land"
                    console_messege_timer_start =  time.time()
                elif controller.right:#activate CNN auto pilot
                    auto_pilot=True
                elif controller.left:#back to manual control
                    auto_pilot=False

                #control offset adjustment
                elif(msvcrt.kbhit()):
                    key = msvcrt.getch()
                    if(key.decode() == 'w'):
                        pitch_offset = pitch_offset + 5
                    elif(key.decode() == 's'):
                        pitch_offset = pitch_offset -5
                    elif(key.decode() == 'a'):
                        roll_offset = roll_offset - 5
                    elif(key.decode() == 'd'):
                        roll_offset = roll_offset + 5
                    elif(key.decode() == 'q'):
                        rotate_offset = rotate_offset - 5
                    elif(key.decode() == 'e'):
                        rotate_offset = rotate_offset + 5
                
                else:#flying control
                    if auto_pilot:#auto piloting
                        if abs(controller.a_joystick_right_x)<0.1 and abs(controller.a_joystick_right_y)<0.1 and abs(controller.a_trigger)<0.1:
                            #not being interrupt
                            #auto_pilot controll method
                            pitch=1500+pitch_offset
                            roll=1500+roll_offset
                            rotate=1500+rotate_offset
                            if(frontcontrol == 1):
                                pitch = 1520+pitch_offset
                                frontcontrol = not frontcontrol

                            if(top1 == 'front'):
                                pitch = 1530+pitch_offset
                                prestate = 'front'
                                # if(prestate == 'front2'):
                                #     pitch = 1600+pitch_offset
                                #     prestate = 'front3'
                                # elif(prestate == 'front3'):
                                #     pitch = 1500+pitch_offset
                                #     prestate == 'front' 
                                # else:
                                #     pitch = 1600+pitch_offset
                                #     prestate = 'front2'
                            elif(top1 == 'stop'):
                                if(prestate == 'stop2'):
                                    pitch = 1500+pitch_offset
                                    prestate = 'stop3'
                                elif(prestate == 'stop3'):
                                    pitch = 1500+pitch_offset
                                    prestate = 'stop'
                                else:
                                    pitch = 1500+pitch_offset
                                    prestate = 'stop2'
                            elif(top1 == 'left'):
                                rotate = 1350+rotate_offset
                            elif(top1 == 'right'):
                                rotate = 1650+rotate_offset
                            
                            #Top2 controll
                            if(top2 == 'front'):
                                pitch = pitch
                                prestate2 = 'front'
                                # if(prestate2 == 'front2'):
                                #     pitch = 1550+pitch_offset
                                #     prestate2 = 'front3'
                                # elif(prestate2 == 'front3'):
                                #     pitch = 1500+pitch_offset
                                #     prestate2 == 'front' 
                                # else:
                                #     pitch = 1550+pitch_offset
                                #     prestate2 = 'front2'
                            elif(top2 == 'stop'):
                                if(prestate2 == 'stop2'):
                                    pitch = 1500 + pitch_offset
                                    prestate2 = 'stop3'
                                elif(prestate2 == 'stop3'):
                                    pitch = 1500 + pitch_offset
                                    prestate2 = 'stop'
                                else:
                                    pitch = 1500 + pitch_offset
                                    prestate2 = 'stop2'
                            elif(top2 == 'left'):
                                rotate = rotate - 50
                            elif(top2 == 'right'):
                                rotate = rotate + 50

                            flying_state='auto_pilot'


                        else:#interrupt auto pilot
                            pitch=int(controller.a_joystick_right_y*((-1)*sensitivity)+1500+pitch_offset)
                            rotate=int(controller.a_trigger*((-1)*sensitivity)+1500+rotate_offset)

                            flying_state='interrupt'
                            
                        if abs(controller.a_joystick_left_y)>=0.1 and throttle>=1000 and throttle<=2000:
                            throttle=throttle+int(controller.a_joystick_left_y*(-10))
                        elif throttle>2000:
                            throttle=2000
                        elif throttle<1000:
                            throttle=1000
                        roll=int(controller.a_joystick_right_x*sensitivity+1500+roll_offset)


                    else:#manual control
                        roll=int(controller.a_joystick_right_x*sensitivity+1500+roll_offset)
                        pitch=int(controller.a_joystick_right_y*((-1)*sensitivity)+1500+pitch_offset)
                        rotate=int(controller.a_trigger*((-1)*sensitivity)+1500+rotate_offset)
                        if abs(controller.a_joystick_left_y)>=0.1 and throttle>=1000 and throttle<=2000:
                            throttle=throttle+int(controller.a_joystick_left_y*(-10))
                        elif throttle>2000:
                            throttle=2000
                        elif throttle<1000:
                            throttle=1000

                        flying_state='prepare'
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
                data = [roll,pitch,rotate,throttle]
                butterfly.sendCMD(8,MultiWii.SET_RAW_RC,data)        
                
                textPrint.print(screen, "Console Messege: {}".format(console_messege) )

                textPrint.print(screen, " {}".format(" ") )
                
                textPrint.print(screen, "Roll:      {}".format(roll) )
                textPrint.print(screen, "Pitch:     {}".format(pitch) )
                textPrint.print(screen, "Rotate:    {}".format(rotate) )
                textPrint.print(screen, "Throttle: {}".format(throttle) )
                
                textPrint.print(screen, " {}".format(" ") )
                
                textPrint.print(screen, "Sensitivity: {}".format(sensitivity) )

                textPrint.print(screen, " {}".format(" ") )
                if auto_pilot:
                    textPrint.print(screen, "Status: CNN Auto Pilot {}".format(" "))
                else:
                    textPrint.print(screen, "Status: Manual Controll {}".format(" "))
                    
                textPrint.print(screen, " {}".format(" ") )
                
                textPrint.print(screen, "Top1: %s , Top2: %s" %(top1,top2) )

                textPrint.print(screen, " {}".format(" ") )

                textPrint.print(screen, "Flower Probability: %s" %(flower_prob[0]) )

                textPrint.print(screen, " {}".format(" ") )
                
                textPrint.print(screen, "Runtime: {}".format(time.time()-runtime) )
        
                # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
                
                # Go ahead and update the screen with what we've drawn.
                pygame.display.flip()
                
                #recording flight control signal
                if throttle!=1000:
                    control_signal_log["%.2f" % loop_time]=data
                    #captured_image_log["%.2f" % loop_time]=image
                    predicted_probability_log["%.2f" % loop_time]=prediction
                    top_label_log["%.2f" % loop_time]=[top1,top2]
                    flying_state_log["%.2f" % loop_time]=flying_state
                    flower_probability_log["%.2f" % loop_time]=flower_prob
                # Limit to 20 frames per second
                clock.tick(10)
                
        except Exception as error:
            print ("Error on Main: "+str(error))
            data = [1500,1500,1500,1000]
            butterfly.sendCMD(8,MultiWii.SET_RAW_RC,data)
            idle=True
            done=True
            
    
        
        cap.release()
        cv2.destroyAllWindows()
        
        butterfly.disarm()
        time.sleep(1)
        butterfly.disarm()
        time.sleep(1)
        butterfly.disarm()
        

    
        if len(control_signal_log)>0 and len(predicted_probability_log)>0 and len(top_label_log)>0 and len(flying_state_log)>0:

            #calculate auto pilot accuracy by the percentage of not inerrupted auto pilot loops during flight
            auto_pilot_counter=0
            interrupt_counter=0
            for item in flying_state_log:
                if flying_state_log[item]=='auto_pilot':
                    auto_pilot_counter=auto_pilot_counter+1
                elif flying_state_log[item]=='interrupt':
                    interrupt_counter=interrupt_counter+1

            auto_pilot_accuracy=auto_pilot_counter/(auto_pilot_counter+interrupt_counter)
            
            print('Auto Pilot Accuracy: %0.3f' % auto_pilot_accuracy)

            file_name=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            
            #writing flying log to a csv file
            with open('control_signal_log/'+file_name+'.csv', 'w', newline='') as csvfile:
                fieldnames=['time','roll','pitch','rotate','throttle','front','left','right','stop','flower','top1','top2','flying state']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
                writer.writeheader()
                for item in control_signal_log:
                    writer.writerow({'time':item,'pitch':control_signal_log[item][0],'roll':control_signal_log[item][1],'rotate':control_signal_log[item][2],'throttle':control_signal_log[item][3],'front':predicted_probability_log[item][0],'left':predicted_probability_log[item][1],'right':predicted_probability_log[item][2],'stop':predicted_probability_log[item][3],'flower':flower_probability_log[item],'top1':top_label_log[item][0],'top2':top_label_log[item][1],'flying state':flying_state_log[item]})
        
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
