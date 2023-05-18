import utils
import servo
import sounds
import camera
import movements
import traceback
from enum import Enum
import time


class ProcessState(Enum):
    INIT = 0
    SELFTEST = 1
    STANDBY = 2
    DETECTED_MOVEMENT = 3
    PREPARE_FOR_SEARCHING_TAGET = 4
    SEARCHING_TARGET = 5
    TARGET_TRACKING = 6
    TARGET_LOCKED = 7
    TARGET_LOST = 8
    ERROR = 9
    PARTY_MODE = 10



def start_up():
    # Start pigpio and check if its running correctly.
    status = servo.start_gpio()
    if status != 0:
        return "start_gpio :" + str(status)
    # Start the video stream in a thread
    status = camera.start_video_thread()
    if status != 0:
        return "start_video: " + str(status)
    # Let the camera stream startup properly
    time.sleep(2)
    # If video is running, start detecting thread
    status = camera.start_detection_thread()
    if status != 0:
        return "start_detection" + str(status)
    # All good, return 0
    return 0

def check_threads():
    # Check if all threads are still running
    status = 2
    if camera.thread_video_running == True:
        status = 1
    if camera.thread_detection_running == True:
        status = 0
    return status

def kill_all_threads():
    camera.stop_video_thread()
    camera.stop_detection_thread()
    return 0


def process_manager():
    State = None
    Error_raised_at = None
    Search_timeout_counter_start = 0
    NextState = ProcessState.INIT

    try:
        # Keep the state machine running if all threads are runnings
        while check_threads() == 0:
            # State error controller
            if NextState == ProcessState.ERROR:
                Error_raised_at = State
            # State debug info
            if NextState != State:
                #print ("Last State: " + str(State) + " - Current State: " + str(NextState))
                print ("Current State: " + str(NextState))
            # State controller
            State = NextState
            # Sounds delay controller (runs forever with the main loop, keeps track of delays between sounds)
            sounds.sounds_delay_worker(10000)
            #############################################################
            ####################### State Machine #######################
            #############################################################
            # Initial state, only here once, at the beginning
            if State == ProcessState.INIT:
                servo.home_servos()
                sounds.play_deploy_sound()
                time.sleep(0.5)
                # make sure camera works
                NextState = ProcessState.SELFTEST

            elif State == ProcessState.SELFTEST:
                # Run the self test
                if movements.self_test_run() != 0:
                    NextState = ProcessState.ERROR
                else:
                    NextState = ProcessState.STANDBY

            elif State == ProcessState.STANDBY:
                camera.detecting_movement_controller(True)
                time.sleep(0.05)
                if camera.detected_movement() == True:
                    NextState = ProcessState.DETECTED_MOVEMENT
                else:
                    NextState = ProcessState.STANDBY

            elif State == ProcessState.DETECTED_MOVEMENT:
                camera.detecting_movement_controller(False)
                sounds.play_deploy_sound()
                time.sleep(0.6)
                sounds.play_activated()
                movements.go_to_activated()
                time.sleep(0.3)
                NextState = ProcessState.PREPARE_FOR_SEARCHING_TAGET

            elif State == ProcessState.PREPARE_FOR_SEARCHING_TAGET:
                Search_timeout_counter_start = time.time()
                camera.tracking_controller(True)
                time.sleep(0.2)
                NextState = ProcessState.SEARCHING_TARGET
            
            elif State == ProcessState.SEARCHING_TARGET:
                sounds.play_searching(10000)
                status, angle = camera.tracking_status()
                if status == 1:
                    sounds.stop_searching()
                    time.sleep(0.1)
                    NextState = ProcessState.TARGET_TRACKING
                elif (time.time() - Search_timeout_counter_start) >= utils.SEARCH_TIMEOUT:
                    camera.tracking_controller(False)
                    sounds.stop_searching()
                    time.sleep(0.5) # Gives us some time to stop any already playing sounds
                    sounds.play_deactivated()
                    movements.go_to_standby()
                    NextState = ProcessState.STANDBY
                else:
                    NextState = ProcessState.SEARCHING_TARGET

            elif State == ProcessState.TARGET_TRACKING:
                sounds.play_target_found()
                time.sleep(0.2)
                status, angle = camera.tracking_status()
                if   status == 1:
                    movements.go_to_target_tracking(angle)
                    NextState = ProcessState.TARGET_LOCKED
                elif status == -1:
                    NextState = ProcessState.PREPARE_FOR_SEARCHING_TAGET

            elif State == ProcessState.TARGET_LOCKED:
                    sounds.play_firing()
                    servo.guns_lights(128)
                    movements.go_to_target_firing(5)
                    sounds.stop_firing()
                    servo.guns_lights(0)
                    NextState = ProcessState.TARGET_LOST
            
            elif State == ProcessState.TARGET_LOST:
                sounds.play_target_lost()
                time.sleep(0.2)
                movements.go_to_target_lost()
                camera.tracking_finished()
                NextState = ProcessState.PREPARE_FOR_SEARCHING_TAGET

            elif State == ProcessState.PARTY_MODE:
                party_song = utils.OPERA
                sounds.play_party(party_song)
                movements.go_to_party(party_song)
                time.sleep(0.1) # Gives us some time to stop partying
                sounds.play_deactivated()
                movements.go_to_standby()
                NextState = ProcessState.STANDBY
                
            elif State == ProcessState.ERROR:
                time.sleep(1)
                print ("Error at: " + str(Error_raised_at))
                sounds.play_error_sound()
                time.sleep(2)
                break

        print("Process Manager stopped with an error")
        kill_all_threads()
        servo.disable_servos()
        return 1

    except Exception as e:
        print ("Error while in State: " + str(State) + " NextState: " + str(NextState))
        traceback.print_exc()
        servo.disable_servos()
        kill_all_threads()
        return -1
        ########!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##########TEMP CHANGE TO 1 WHEN THE STARTER SCRIPT IS ADDED ####
