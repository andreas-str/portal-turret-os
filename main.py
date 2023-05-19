import statemachine
import sys
import servo


def main():
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
            return 1
        else:
            print("State Machine exited with a unrecoverrable error :(")
            return -1
    else:
        print("Error starting up.")
        return 2

try:
    main()
except KeyboardInterrupt:
    print(" Exited from Ctrl C")
    servo.kill_servos_and_leds()
    sys.exit()
