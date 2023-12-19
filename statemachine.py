import utils
import servo
import sounds
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
    DUMMY_SEARCH = 10
    PARTY_MODE = 11

def start_up():
    # Start pigpio and check if its running correctly.
    status = servo.start_gpio()
    if status != 0:
        return "start_gpio :" + str(status)
    return 0

def process_manager():
    State = None
    Error_raised_at = None
    NextState = ProcessState.INIT
    Search_timeout_counter_start = 0
    Detected = False

    try:
        # Keep the state machine running
        while True:
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
                servo.amp_power(1)
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
                servo.amp_power(0)
                time.sleep(1)
                NextState = ProcessState.STANDBY
                if Detected == True:
                    servo.amp_power(1)
                    NextState = ProcessState.DETECTED_MOVEMENT

            elif State == ProcessState.DETECTED_MOVEMENT:
                sounds.play_deploy_sound()
                time.sleep(0.6)
                sounds.play_activated()
                movements.go_to_activated()
                time.sleep(0.3)
                NextState = ProcessState.SEARCHING_TARGET

            elif State == ProcessState.SEARCHING_TARGET:
                sounds.play_searching(5)
                movements.go_to_searching()
                time.sleep(1)
                if (time.time() - Search_timeout_counter_start) >= utils.SEARCH_TIMEOUT:
                    sounds.stop_searching()
                    time.sleep(1) # Gives us some time to stop any already playing sounds
                    sounds.play_deactivated()
                    movements.go_to_standby()
                    time.sleep(1)
                    NextState = ProcessState.STANDBY
                else:
                    NextState = ProcessState.SEARCHING_TARGET
##############################################################################################
##############################################################################################
            elif State == ProcessState.TARGET_TRACKING:
                sounds.play_target_found()
                time.sleep(1)
                NextState = ProcessState.TARGET_LOCKED

            elif State == ProcessState.TARGET_LOCKED:
                    sounds.play_firing()
                    servo.guns_lights(128)
                    movements.go_to_target_firing(5)
                    sounds.stop_firing()
                    servo.guns_lights(0)
                    NextState = ProcessState.STANDBY

            elif State == ProcessState.PARTY_MODE:
                party_song = utils.WIFE
                movements.go_to_activated()
                sounds.play_party(party_song)
                movements.go_to_party(party_song)
                time.sleep(20) # Gives us some time to stop partying
                sounds.play_deactivated()
                movements.go_to_standby()
                time.sleep(1)
                NextState = ProcessState.STANDBY
##############################################################################################
##############################################################################################
            elif State == ProcessState.ERROR:
                time.sleep(1)
                print ("Error at: " + str(Error_raised_at))
                servo.amp_power(1)
                sounds.play_error_sound()
                time.sleep(2)
                break

        print("Process Manager stopped with an error")
        servo.amp_power(1)
        servo.disable_servos()
        sounds.play_restarting_sound()
        time.sleep(2)
        servo.amp_power(0)
        return 1

    except Exception as e:
        print ("Error while in State: " + str(State) + " NextState: " + str(NextState))
        traceback.print_exc()
        servo.amp_power(1)
        servo.disable_servos()
        sounds.play_error_sound()
        time.sleep(2)
        servo.amp_power(0)
        return -1
        ########!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##########TEMP CHANGE TO 1 WHEN THE STARTER SCRIPT IS ADDED ####
