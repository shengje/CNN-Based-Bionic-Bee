# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 14:13:52 2017

@author: 蔡永聿
"""

import pygame,time,datetime,csv
from pymultiwii import MultiWii

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 80)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 50
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10


pygame.init()
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()


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
		outstr = ""
		
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
    
# Set the width and height of the screen [width,height]
size = [1000, 450]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Control Panel")

#Loop until the user clicks the close button.
done = False

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)


if __name__ == "__main__":
    
    screen.fill(WHITE)
    textPrint.reset()

    
    butterfly = MultiWii("COM5")
    print("Butterfly Connected")
    time.sleep(1)
    controller=xbox1()
    print("Controller Connected")
    time.sleep(1)
    sensitivity=200 #max 500
    print('Default Sensitivity : %d' % sensitivity)
    time.sleep(1)

    roll=1500
    pitch=1500
    rotate=1500
    throttle=1000
    
    butterfly.disarm()
    
    console_messege_timer_start=0
    auto_land=0
    
    control_signal_log={}
    control_signal_log_timer_start=time.time()
    
    try:
        # -------- Main Program Loop -----------
        while done==False:
            # EVENT PROCESSING STEP
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    done=True # Flag that we are done so we exit this loop
            
            # DRAWING STEP
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            screen.fill(WHITE)
            textPrint.reset()
                         
            controller.update()
            
            if time.time() - console_messege_timer_start > 2:
                console_messege=" "
                
            if controller.B:
                butterfly.arm()
                console_messege="Armed."
                console_messege_timer_start =  time.time()
            elif controller.A:
                butterfly.disarm()
                console_messege="Disarmed."
                console_messege_timer_start =  time.time()
            elif controller.Y:
                done=True        	
            #example of 4 RC channels to be send
            elif controller.X:
                pitch=1500
                roll=1500
                rotate=1500
                throttle=1000 
            elif controller.rb:
                if sensitivity<500:
                    sensitivity=sensitivity+50
            elif controller.lb:
                if sensitivity>100:
                    sensitivity=sensitivity-50
            elif controller.up:
                throttle=1550
                console_messege="Auto Take Off"
                console_messege_timer_start =  time.time()
            elif controller.down or auto_land==1:
                if throttle>1400:
                    auto_land=1
                    throttle = throttle - 5
                else:
                    time.sleep(1)
                    auto_land=0
                console_messege="Auto Land"
                console_messege_timer_start =  time.time()
            else:
                '''Control Method of Project'''
#                rotate=int(controller.a_joystick_right_x*sensitivity+1500)
#                pitch=int(controller.a_joystick_right_y*((-1)*sensitivity)+1500)
#                roll=int(controller.a_trigger*((-1)*sensitivity)+1500)
#                if abs(controller.a_joystick_left_y)>=0.1 and throttle>=1000 and throttle<=2000:
#                    throttle=throttle+int(controller.a_joystick_left_y*(-5))
#                elif throttle>2000:
#                    throttle=2000
#                elif throttle<1000:
#                    throttle=1000
                '''American Hand(project version)'''
                roll=int(controller.a_joystick_right_x*sensitivity+1500)
                pitch=int(controller.a_joystick_right_y*((-1)*sensitivity)+1500)
                rotate=int(controller.a_trigger*((-1)*sensitivity)+1500)
                if abs(controller.a_joystick_left_y)>=0.1 and throttle>=1000 and throttle<=2000:
                    throttle=throttle+int(controller.a_joystick_left_y*(-5))
                elif throttle>2000:
                    throttle=2000
                elif throttle<1000:
                    throttle=1000

                
                
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
    
            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
            
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            
            #recording flight control signal
            if throttle!=1000:
                control_signal_log["%.2f" % (time.time()-control_signal_log_timer_start)]=data
        
            # Limit to 20 frames per second
            clock.tick(20)
            
    except Exception as error:
        print ("Error on Main: "+str(error))


    butterfly.disarm()
    time.sleep(1)
    butterfly.disarm()
    time.sleep(1)
    butterfly.disarm()    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

if len(control_signal_log)>0:
    file_name=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    with open('control_signal_log/'+file_name+'.csv', 'w', newline='') as csvfile:
        fieldnames=['time','roll','pitch','rotate','throttle']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()
        for item in control_signal_log:
            writer.writerow({'time':item,'pitch':control_signal_log[item][0],'roll':control_signal_log[item][1],'rotate':control_signal_log[item][2],'throttle':control_signal_log[item][3]})
        