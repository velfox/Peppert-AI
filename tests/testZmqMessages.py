import zmq

def handle_transcript_message(message):
    print(f"Handling transcript message: {message}")
    # Voeg hier de logica toe voor transcript berichten
    # Bijv. verwerken van transcripties

def handle_mic_control_message(message):
    print(f"Handling mic control message: {message}")
    if message == "enable_mic":
        print("Microphone enabled")
        # Voeg hier de logica toe om de microfoon in te schakelen
    elif message == "disable_mic":
        print("Microphone disabled")
        # Voeg hier de logica toe om de microfoon uit te schakelen
    else:
        print(f"Unknown mic control message: {message}")

def handle_processing_status_message(message):
    print(f"Handling processing status message: {message}")
    if message == "processing_started":
        print("Processing started")
        # Voeg hier de logica toe voor wanneer de verwerking begint
    elif message == "processing_done":
        print("Processing done")
        # Voeg hier de logica toe voor wanneer de verwerking is voltooid
    else:
        print(f"Unknown processing status message: {message}")

def handle_response_message(message):
    print(f"Handling response message: {message}")
    # Voeg hier de logica toe voor het verwerken van de ChatGPT-reactie

def handle_user_detected_message(message):
    print(f"Handling user detected message: {message}")

def handle_tablet_webpage_started_message(message):
    print(f"Handling tablet webpage started message: {message}")

def handle_select_assistant_message(message):
    print(f"Handling select assistant message: {message}")

def handle_end_conversation_message(message):
    print(f"Handling end conversation message: {message}")

def handle_humendetaction_message(message):
    print(f"Handling human detection message: {message}")

def main():
    context = zmq.Context()
    
    # Create a ZeroMQ subscriber socket
    subscriber_socket = context.socket(zmq.SUB)
    subscriber_socket.connect("tcp://127.0.0.1:3001")
    subscriber_socket.connect("tcp://127.0.0.1:3004")
    
    # Subscribe to the relevant topics
    topics = [
        'transcript_topic', 'mic_control_topic', 'processing_topic', 'response_topic',
        'user_detected_topic', 'tablet_webpage_started_topic', 'select_assistant_topic', 
        'end_conversation_topic', 'humendetaction'
    ]
    for topic in topics:
        subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    print(f"Listening for messages on topics: {', '.join(topics)}...")

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
        elif topic == 'user_detected_topic':
            handle_user_detected_message(message)
        elif topic == 'tablet_webpage_started_topic':
            handle_tablet_webpage_started_message(message)
        elif topic == 'select_assistant_topic':
            handle_select_assistant_message(message)
        elif topic == 'end_conversation_topic':
            handle_end_conversation_message(message)
        elif topic == 'humendetaction':
            handle_humendetaction_message(message)
        else:
            print(f"Unknown topic: {topic}")

if __name__ == "__main__":
    main()
