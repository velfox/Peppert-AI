import zmq
import json
import threading
import time
from naoqi import ALProxy

# NAOqi Proxies
PEPPER_IP = "10.255.30.234"  # Replace with your Pepper's actual IP address
PEPPER_PORT = 9559

try:
    tts = ALProxy("ALAnimatedSpeech", PEPPER_IP, PEPPER_PORT)
    leds = ALProxy("ALLeds", PEPPER_IP, PEPPER_PORT)
except Exception as e:
    print("Could not create proxy to Pepper. Error: ", e)
    exit(1)

# ZeroMQ context and sockets
context = zmq.Context()
subscriber_socket = context.socket(zmq.SUB)
subscriber_socket.connect("tcp://127.0.0.1:3004")
subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, u'')

# Global status variables
micStatus = True
processing = False

def control_microphone(enable):
    global micStatus
    micStatus = enable
    if enable:
        leds.off("AllLeds")
        leds.fadeRGB("FaceLeds", 0x00FF00, 1)  # Green
    else:
        leds.off("AllLeds")
        leds.fadeRGB("FaceLeds", 0xFF0000, 1)  # Red

def send_processing_status(started):
    global processing
    processing = started
    if started:
        leds.off("AllLeds")
        leds.post.rotateEyes(0xFFFF00, 1, 1)  # Yellow rotating eyes
    else:
        leds.off("AllLeds")
        leds.fadeRGB("FaceLeds", 0x0000FF, 1)  # Blue

def speak(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    tts.say("\\pau=1000\\" + text)

def idle_animation():
    while True:
        if not micStatus and not processing:
            leds.randomEyes(3)
        time.sleep(1)

def process_message(topic, message):
    global micStatus, processing

    if topic == 'mic_control_topic':
        if message == 'enable_mic':
            control_microphone(True)
        elif message == 'disable_mic':
            control_microphone(False)
    elif topic == 'processing_topic':
        if message == 'processing_started':
            send_processing_status(True)
        elif message == 'processing_done':
            send_processing_status(False)
    elif topic == 'response_topic':
        speak(message)

def main():
    idle_thread = threading.Thread(target=idle_animation)
    idle_thread.setDaemon(True)
    idle_thread.start()

    while True:
        topic, message = subscriber_socket.recv_multipart()
        topic = topic.decode('utf-8')
        message = message.decode('utf-8')
        
        process_message(topic, message)

if __name__ == "__main__":
    main()
