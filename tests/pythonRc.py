import zmq

def main():
    # Create a ZeroMQ context
    context = zmq.Context()

    # Create a ZeroMQ subscriber socket
    socket = context.socket(zmq.SUB)

    # Connect to the publisher
    socket.connect("tcp://127.0.0.1:3001")

    # Subscribe to the topic (empty string subscribes to all topics)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'transcript_topic')

    print("Listening for messages on topic 'transcript_topic'...")

    while True:
        # Receive a message
        topic, message = socket.recv_multipart()
        print(f"Received message on topic '{topic.decode()}': {message.decode()}")

if __name__ == "__main__":
    main()
