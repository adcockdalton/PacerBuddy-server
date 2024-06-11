from gpiozero import Robot
import sys
from time import sleep
import signal
import time
from HCSR04_python_lib import HCSR04
import os
from supabase import create_client, Client
from dotenv import load_dotenv
# Load the .env file
load_dotenv()

hcsr_sensor = HCSR04(trigger_pin=8, echo_pin=7)

distTraveled = 0
timeTraveled = 0
pace = 0

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def cleanup():
    print("Cleaning up before exit...")
    # Perform any cleanup actions here
    # For example, closing files, releasing resources, etc.
    print(f"Cleaning up with distTraveled={distTraveled} and timeTraveled={timeTraveled}")

def signal_handler():
    def handler(sig, frame):
        print("Received signal to terminate. Performing cleanup...")
        cleanup()
        sys.exit(0)
    return handler

def main():
    global pace, timeTraveled

    if len(sys.argv) != 2:
        print("Usage: python rover.py <pace>")
        return
    
    if float(sys.argv[1]) < 0 or float(sys.argv[1]) > 10:
        print("Usage: pace should be a positive float")
        return

    try:
        
        pace = ( (100)/ (200*(11-float(sys.argv[1]))) )
        front = Robot(left=(24,23), right=(9,10))
        rear = Robot(left=(2,3), right=(17,27))

        timeTraveled = 0
        
        signal.signal(signal.SIGINT, signal_handler())

        rear.forward(pace)
        front.forward(pace)
        
        startTime = time.time()
        paceArr = []
        timeArr = []
        
        while True:
            try:
                distance = hcsr_sensor.get_distance(sample_size=2, decimal_places=2)
                # print("pace:", pace)
                # print("distance", distance)
                # print()

                pace = max(( (100-distance)/ (100*(11-float(sys.argv[1]))) ), 0)
                timeTraveled = round(time.time() - startTime)

                paceArr.append(pace)
                timeArr.append(timeTraveled)
                
                
                rear.forward(pace)
                front.forward(pace)
                print("API call made")
                data, count = supabase.table("Session")\
                    .update({'pace': paceArr, 'time': timeArr})\
                    .eq('id', 123)\
                    .execute()
                # print(data, count)


                    # try:
                    #     result = supabase.rpc("append_distance", {"session_id": 123, "new_distance": pace * timeTraveled })
                    #     print(result)
                    # except Exception as e:
                    #     print("Error making call:", e)

                
                sleep(1)
            except TimeoutError as ex:
                print(f'ERROR getting distance: {ex}')

            except OSError as ex:
                print(f'ERROR getting distance: {ex}')
            except KeyboardInterrupt as ex:
                print(f'Measurement stopped. {ex}')

    except:
        print("Error within python script for rover")

if __name__ == "__main__":
    main()
