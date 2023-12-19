import statemachine
import sys
import servo
import sounds
import time


def main():
    while True:
        print("--------------------------------------")
        print("--------- Aperture Science -----------")
        print("----------- Sentry Turret ------------")
        print("--------------------------------------")
        print("Turret OS Version: 0.2 Alpha")
        print("Starting up...")
        status = statemachine.start_up()
        if status == 0:
            print("Startup complete. Starting state machine...")
            fault = statemachine.process_manager()
            if fault == 1:
                print("State Machine exited with a recoverable error, restarting application...")
                continue
            else:
                print("State Machine exited with a unrecoverrable error :(")
                servo.amp_power(1)
                sounds.play_error_sound()
                time.sleep(2)
                servo.amp_power(0)
                return -1
        else:
            print("Error starting up.")
            servo.amp_power(1)
            sounds.play_error_sound()
            time.sleep(2)
            servo.amp_power(0)
            return 2

try:
    main()
        
except KeyboardInterrupt:
    servo.amp_power(1)
    sounds.play_error_sound()
    time.sleep(2)
    print(" Exited from Ctrl C")
    servo.kill_servos_and_leds()
    servo.amp_power(0)
    sys.exit()
