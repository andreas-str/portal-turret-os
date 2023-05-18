import utils
import servo
import time
import random

def self_test_run():
    # Test wing extension and eye LEDs
    status = servo.eye_light(255)
    status = servo.move_wings(utils.BOTH_WINGS, 100)
    # Test wing rotation
    status = servo.rotate_wings(utils.WING_UP, 60)
    status = servo.rotate_wings(utils.WING_DOWN, 60)
    status = servo.rotate_wings(utils.WING_DOWN, 0)
    # Test Turret rotation
    status = servo.rotate_turret(utils.TURRET_LEFT, 50)
    status = servo.rotate_turret(utils.TURRET_RIGHT, 50)
    status = servo.rotate_turret(utils.TURRET_RIGHT, 0)
    # Test gun lights
    servo.guns_lights(100)
    time.sleep(0.1)
    # Restore to default positions
    servo.guns_lights(0)
    status = servo.move_wings(utils.BOTH_WINGS, 0)
    servo.eye_light(0)
    if status != 0:
        return -1
    return 0

def go_to_standby():
    servo.guns_lights(0)
    # Go to zero position
    status = servo.rotate_wings(utils.WING_DOWN, 0)
    status = servo.rotate_turret(utils.TURRET_RIGHT, 0)
    time.sleep(0.2)
    # Wait a bit and then retract the wings
    status = servo.move_wings(utils.BOTH_WINGS, 0)
    time.sleep(0.3)
    # Wait a bit and then disable the eye
    servo.eye_light(0)
    if status != 0:
        return -1
    return 0

def go_to_activated():
    # Enable eye
    servo.eye_light(255)
    # Extend wings fully
    status = servo.move_wings(utils.BOTH_WINGS, 100)
    time.sleep(0.2)
    if status != 0:
        return -1
    return 0

def go_to_searching():
    wing_rotate_pos = random.randint(0,80)
    wing_rotate_dir = random.randint(utils.WING_UP,utils.WING_DOWN)
    turret_rotate_pos = random.randint(0,50)
    turret_rotate_dir = random.randint(utils.TURRET_LEFT,utils.TURRET_RIGHT)
    status = servo.rotate_wings(wing_rotate_dir, wing_rotate_pos)
    status = servo.rotate_turret(turret_rotate_dir, turret_rotate_pos)
    if status != 0:
        return -1
    return 0

def go_to_target_tracking(angle):
    print("provided angle:" + str(angle))
    cur_pos = 0
    if angle > 100:
        cur_pos = angle - 100
        servo.rotate_turret(utils.TURRET_LEFT, cur_pos)
    elif angle < 100 and angle > 0:
        cur_pos = angle + 100
        servo.rotate_turret(utils.TURRET_RIGHT, cur_pos)
    return 0

def go_to_target_firing(max_time):
    runtime = 0
    while runtime < max_time:
        wing_rotate_pos = random.randint(0,20)
        wing_rotate_dir = random.randint(utils.WING_UP,utils.WING_DOWN)
        status = servo.rotate_wings(wing_rotate_dir, wing_rotate_pos)
        time.sleep(0.2)
        runtime = runtime + 1

def go_to_target_lost():
    wing_rotate_pos = random.randint(0,20)
    wing_rotate_dir = random.randint(utils.WING_UP,utils.WING_DOWN)
    turret_rotate_pos = 0
    turret_rotate_dir = utils.TURRET_LEFT
    status = servo.rotate_wings(wing_rotate_dir, wing_rotate_pos)
    status = servo.rotate_turret(turret_rotate_dir, turret_rotate_pos)
    time.sleep(1)
    if status != 0:
        return -1
    return 0

###################################################
##################### Extras ######################
###################################################

def go_to_picked_up():
    return 0

def go_to_dropped():
    return 0

def go_to_party(selected_party):
    return 0
