import zmq
import os
import time
from pathlib import Path
import pyaudio
from openai import OpenAI

# Setup OpenAI API key
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup ZeroMQ context and sockets
context = zmq.Context()
subscriber_socket = context.socket(zmq.SUB)
subscriber_socket.connect("tcp://127.0.0.1:3001")  # Ensure this matches your setup
subscriber_socket.connect("tcp://127.0.0.1:3004")  # Connect to response topic

# Subscribe to the relevant topics
topics = ['transcript_topic', 'mic_control_topic', 'processing_topic', 'response_topic']
for topic in topics:
    subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

print(f"Listening for messages on topics: {', '.join(topics)}...")

def stream_to_speakers(response):
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    start_time = time.time()
    print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
    for chunk in response.iter_bytes(chunk_size=1024):
        player_stream.write(chunk)
    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")

def handle_transcript_message(message):
    print(f"Handling transcript message: {message}")
    # Process transcript messages if needed

def handle_mic_control_message(message):
    print(f"Handling mic control message: {message}")
    if message == "enable_mic":
        print("Microphone unmuted")
    elif message == "disable_mic":
        print("Microphone muted")
    else:
        print(f"Unknown mic control message: {message}")

def handle_processing_status_message(message):
    print(f"Handling processing status message: {message}")
    if message == "processing_started":
        print("Processing started")
    elif message == "processing_done":
        print("Processing done")
    else:
        print(f"Unknown processing status message: {message}")

def handle_response_message(message):
    print(f"Handling response message: {message}")

    # Create the TTS audio and stream to speakers
    try:
        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            response_format="pcm",  # similar to WAV, but without a header chunk at the start.
            input=message,
        ) as response:
            stream_to_speakers(response)
    except Exception as e:
        print(f"Error generating TTS: {e}")

def main():
    while True:
        topic, message = subscriber_socket.recv_multipart()
        topic = topic.decode()
        message = message.decode()
        print(f"Received message on topic '{topic}': {message}")

        # Call different handlers based on the topic
        if topic == 'transcript_topic':
            handle_transcript_message(message)
        elif topic == 'mic_control_topic':
            handle_mic_control_message(message)
        elif topic == 'processing_topic':
            handle_processing_status_message(message)
        elif topic == 'response_topic':
            handle_response_message(message)
        else:
            print(f"Unknown topic: {topic}")

if __name__ == "__main__":
    main()
