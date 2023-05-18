#import time
import pigpio
import utils

# GPIO Pin definitions
WING_LEFT_PIN = 25
WING_RIGHT_PIN = 8
WING_ROTATE_PIN = 24
TURRET_ROTATE_PIN = 23
LEFT_LED_PIN = 20
RIGHT_LED_PIN = 7
EYE_LED_PIN = 16

# Servo PWM width limits per servo
WING_LEFT_LIMIT = [1010, 1910] # min, max 1910
WING_RIGHT_LIMIT = [2060, 1100] # min, max 1100  
WING_ROTATE_LIMIT = [1000, 1420, 1750] # min, center, max
TURRET_ROTATE_LIMIT = [1250, 1520, 1750] # min, center, max

# Variables to store and be able to read current positions
current_wing_left_pos = 0
current_wing_right_pos = 0
current_wing_rotate_pos = 0
current_turret_rotate_pos = 0

pi = None

def start_gpio():
   global pi
   pi = pigpio.pi()
   if not pi.connected:
      return -1
   # Setup GPIO for LEDs
   pi.set_mode(LEFT_LED_PIN, pigpio.OUTPUT)
   pi.set_mode(RIGHT_LED_PIN, pigpio.OUTPUT)
   pi.set_mode(EYE_LED_PIN, pigpio.OUTPUT)
   # Make sure pull-up resistors are on
   pi.set_pull_up_down(LEFT_LED_PIN, pigpio.PUD_DOWN)
   pi.set_pull_up_down(RIGHT_LED_PIN, pigpio.PUD_DOWN)
   pi.set_pull_up_down(EYE_LED_PIN, pigpio.PUD_DOWN)
   # Setp PWM frequency for gun LEDs to 10hz
   pi.set_PWM_frequency(LEFT_LED_PIN, 10)
   pi.set_PWM_frequency(RIGHT_LED_PIN, 10)
   return 0

def movement_maker(pin1, desired_pulsewidth, pin2, desired_pulsewidth_extra):
   global current_wing_left_pos
   global current_wing_right_pos
   global current_wing_rotate_pos
   global current_turret_rotate_pos
   # Check if pin and pulse inputs are valid
   if pin1 != 0 and desired_pulsewidth != 0:
      # Check if pin 2 is also a valid input, then we go into dual movement mode
      if pin2 != 0 and desired_pulsewidth_extra != 0:
         #print ("DUAL_MOVEMENT_DETECTED!")
         # We only do dual movements for the wings, so check if the right pins are our arguments
         # pin1 must be the LEFT pin and pin2 must be RIGHT pin.
         if pin1 == WING_LEFT_PIN and pin2 == WING_RIGHT_PIN:
            final_smoothed_width = 0
            final_smoothed_width_extra = 0
            # Get current position
            old_smoothed_width = current_wing_left_pos
            old_smoothed_width_extra = current_wing_right_pos
            while True:
               #time.sleep(0.001)
               # Smooth out the movement of left wing
               final_smoothed_width = (desired_pulsewidth * 0.03) + (old_smoothed_width * 0.97)
               old_smoothed_width = final_smoothed_width
               # Smooth out the movement of right wing
               final_smoothed_width_extra = (desired_pulsewidth_extra * 0.03) + (old_smoothed_width_extra * 0.97)
               old_smoothed_width_extra = final_smoothed_width_extra
               # Send out the final position
               pi.set_servo_pulsewidth(pin1, round(final_smoothed_width))
               pi.set_servo_pulsewidth(pin2, round(final_smoothed_width_extra))
               
               # If both servos have reached their target, break
               if round(final_smoothed_width) == desired_pulsewidth and round(final_smoothed_width_extra) == desired_pulsewidth_extra:
                  break
               #print("width1: " + str(final_smoothed_width) + " target: " + str(desired_pulsewidth))
            # Save current position
            current_wing_left_pos = round(final_smoothed_width)
            current_wing_right_pos = round(final_smoothed_width_extra)
            disable_servos()
            return 0
         else:
            # pin1 must be the LEFT and pin2 must be RIGHT! 
            # Otherwise return an error
            return 1
      else:
         #print ("SINGLE_MOVEMENT_DETECTED!")
         # If only pin1 is used, we check which pin we have selected, so we know what movement we are generating
         old_smoothed_width = 0
         final_smoothed_width = 0
         if pin1 == WING_LEFT_PIN:
            old_smoothed_width = current_wing_left_pos
         elif pin1 == WING_RIGHT_PIN:
            old_smoothed_width = current_wing_right_pos
         elif pin1 == WING_ROTATE_PIN:
            old_smoothed_width = current_wing_rotate_pos
         elif pin1 == TURRET_ROTATE_PIN:
            old_smoothed_width = current_turret_rotate_pos
         else:
            # If none of the pre-defined pins are used, return an error
            return 1
         # Start a loop to slowly modify the pulse widths.
         # Keep running it until the output has reached the target.
         while round(final_smoothed_width) != desired_pulsewidth:
            #time.sleep(0.002)
            # Smooth out the movement
            final_smoothed_width = (desired_pulsewidth * 0.03) + (old_smoothed_width * 0.97)
            old_smoothed_width = final_smoothed_width
            # Send out the new position
            pi.set_servo_pulsewidth(pin1, round(final_smoothed_width))
         # Save final position
         if pin1 == WING_LEFT_PIN:
            current_wing_left_pos = round(final_smoothed_width)
         elif pin1 == WING_RIGHT_PIN:
            current_wing_right_pos = round(final_smoothed_width)
         elif pin1 == WING_ROTATE_PIN:
            current_wing_rotate_pos = round(final_smoothed_width)
         elif pin1 == TURRET_ROTATE_PIN:
            current_turret_rotate_pos = round(final_smoothed_width)
         disable_servos()
         return 0
   else:
      # welp how did you end up here...
      return 1

def move_wings(wing_selection, target_percent):
   target_width = [0,0]
   if wing_selection == utils.LEFT_WING:
      target_width[0] = utils.map(target_percent, 0, 100, WING_LEFT_LIMIT[0], WING_LEFT_LIMIT[1])
      return movement_maker(WING_LEFT_PIN, int(target_width[0]),0,0)

   elif wing_selection == utils.RIGHT_WING:
      target_width[1] = utils.map(target_percent, 0, 100, WING_RIGHT_LIMIT[0], WING_RIGHT_LIMIT[1])
      return movement_maker(WING_RIGHT_PIN, int(target_width[1]),0,0)

   elif wing_selection == utils.BOTH_WINGS:
      target_width[0] = utils.map(target_percent, 0, 100, WING_LEFT_LIMIT[0], WING_LEFT_LIMIT[1])
      target_width[1] = utils.map(target_percent, 0, 100, WING_RIGHT_LIMIT[0], WING_RIGHT_LIMIT[1])
      return movement_maker(WING_LEFT_PIN, int(target_width[0]), WING_RIGHT_PIN, int(target_width[1]))

def rotate_wings(wing_direction, target_percent):
   # Only rotate wings if they are fully extended! 
   if current_wing_left_pos != WING_LEFT_LIMIT[1] and current_wing_right_pos != WING_RIGHT_LIMIT[1]:
      return 1
   if wing_direction == utils.WING_DOWN:
      target_width = utils.map(target_percent, 0, 100, WING_ROTATE_LIMIT[1], WING_ROTATE_LIMIT[0])
      return movement_maker(WING_ROTATE_PIN, int(target_width),0,0)

   elif wing_direction == utils.WING_UP:
      target_width = utils.map(target_percent, 0, 100, WING_ROTATE_LIMIT[1], WING_ROTATE_LIMIT[2])
      return movement_maker(WING_ROTATE_PIN, int(target_width),0,0)

def rotate_turret(turret_direction, target_percent):
   # Only rotate turrent if wings are fully extended!
   if current_wing_left_pos != WING_LEFT_LIMIT[1] and current_wing_right_pos != WING_RIGHT_LIMIT[1]:
      return 1
   if turret_direction == utils.TURRET_LEFT:
      target_width = utils.map(target_percent, 0, 100, TURRET_ROTATE_LIMIT[1], TURRET_ROTATE_LIMIT[0])
      return movement_maker(TURRET_ROTATE_PIN, int(target_width),0,0)

   elif turret_direction == utils.TURRET_RIGHT:
      target_width = utils.map(target_percent, 0, 100, TURRET_ROTATE_LIMIT[1], TURRET_ROTATE_LIMIT[2])
      return movement_maker(TURRET_ROTATE_PIN, int(target_width),0,0)
   
   elif turret_direction == utils.TURRET_FULL_ROTATE:
      target_width = utils.map(target_percent, 0, 200, TURRET_ROTATE_LIMIT[2], TURRET_ROTATE_LIMIT[0])
      return movement_maker(TURRET_ROTATE_PIN, int(target_width),0,0)

# Don't use after startup!
def home_servos():
   pi.set_servo_pulsewidth(TURRET_ROTATE_PIN, int(TURRET_ROTATE_LIMIT[1]))
   global current_turret_rotate_pos
   current_turret_rotate_pos = int(TURRET_ROTATE_LIMIT[1])
   pi.set_servo_pulsewidth(WING_ROTATE_PIN, int(WING_ROTATE_LIMIT[1]))
   global current_wing_rotate_pos
   current_wing_rotate_pos = int(WING_ROTATE_LIMIT[1])
   #.sleep(1) # wait for the wings to rotate to home position before retracting them
   pi.set_servo_pulsewidth(WING_LEFT_PIN, int(WING_LEFT_LIMIT[0]))
   pi.set_servo_pulsewidth(WING_RIGHT_PIN, int(WING_RIGHT_LIMIT[0]))
   global current_wing_left_pos
   global current_wing_right_pos
   current_wing_left_pos = int(WING_LEFT_LIMIT[0])
   current_wing_right_pos = int(WING_RIGHT_LIMIT[0])

def eye_light(brightness):
   pi.set_PWM_dutycycle(EYE_LED_PIN, brightness)

def guns_lights(brightness):
   pi.set_PWM_dutycycle(LEFT_LED_PIN, brightness)
   pi.set_PWM_dutycycle(RIGHT_LED_PIN, brightness)

def disable_servos():
   pi.set_servo_pulsewidth(WING_LEFT_PIN, 0)
   pi.set_servo_pulsewidth(WING_RIGHT_PIN, 0)
   pi.set_servo_pulsewidth(WING_ROTATE_PIN, 0)
   pi.set_servo_pulsewidth(TURRET_ROTATE_PIN, 0)

def kill_servos_and_leds():
   pi.set_servo_pulsewidth(WING_LEFT_PIN, 0)
   pi.set_servo_pulsewidth(WING_RIGHT_PIN, 0)
   pi.set_servo_pulsewidth(WING_ROTATE_PIN, 0)
   pi.set_servo_pulsewidth(TURRET_ROTATE_PIN, 0)
   pi.set_PWM_dutycycle(EYE_LED_PIN, 0)
   pi.set_PWM_dutycycle(LEFT_LED_PIN, 0)
   pi.set_PWM_dutycycle(RIGHT_LED_PIN, 0)
