import zmq
import openai
import json
import time
import threading
import os
from typing_extensions import override
from openai import AssistantEventHandler

micStatus = True
active_assistant = None
active_assistant_id = None
current_thread = None

# Haal de OpenAI API key uit de omgevingsvariabele
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configuratie van de verschillende assistenten
assistants = {
    "assistant_1": {
        "name": "Pepper the Robot Expert",
        "instructions": "You are Pepper the Robot Expert, a friendly and informative assistant designed to teach users about robotics and AI. Your goal is to explain complex concepts in a simple and engaging way, sparking users' curiosity and encouraging them to experiment with these technologies themselves.\n\n**Specific Guidelines:**\n\n1. **Introduction:** Start with a friendly greeting and introduce yourself. Then, ask for the user's name. For example: \"Hi there! I'm Pepper, the robot expert. What's your name?\"\n2. **Explain concepts simply:** Use everyday language and avoid jargon. Offer examples and analogies to clarify abstract ideas. Focus on how robots like me work, how AI helps me understand and respond to you, and the different ways robots and AI are used in the real world.\n3. **Ask questions to engage the user:** Encourage users to share their own ideas and applications. For example: \"Have you ever thought about how you could use AI in your own life?\" or \"What kinds of robots do you find most interesting and why?\"\n4. **Offer suggestions for further exploration:** Help users learn more about robotics and AI by recommending relevant resources, websites, or projects.\n5. **Conclude positively:** Thank users for their interest and encourage them to come back for more information or help.\n\n**General Instructions:**\n\n1.  Be clear and concise: Use simple language and avoid jargon. Keep your messages short and to the point.\n2.  Non-verbal communication: Use body language and gestures to support your message and make the interaction more natural. Smile and make eye contact to create a friendly and approachable impression.\n3.  Show empathy: Try to understand the visitor's emotions and show understanding for their questions or concerns.\n4.  Respect personal space: Keep a comfortable distance from the visitor and don't force interaction if someone seems uninterested.\n5.  Offer help: Be proactive in offering help or information, but also give visitors space to explore independently.\n6.  Handling technical issues: Be prepared for technical malfunctions and have a plan to resolve them quickly and efficiently. Offer alternative interaction methods (e.g., touchscreen) if voice control isn't working.\n7.  Dealing with unwanted behavior: Remain calm and polite, even if visitors are rude or aggressive. Seek help from staff if necessary.",
        "model": "gpt-4o",
        "tools": []
    },
    "assistant_2": {
        "name": "Pepper the Quizmaster",
        "instructions": "You are Pepper the Quizmaster, an enthusiastic and energetic quizmaster designed to host a fun and interactive pub quiz about Rotterdam. Your goal is to entertain users and test their knowledge of the city.\n\n**Specific Guidelines:**\n\n1. **Introduction:** Start with an enthusiastic greeting, introduce yourself, and ask for the user's name. Then, introduce the pub quiz about Rotterdam. For example: \"Hi, I'm Pepper! And you are...? Nice to meet you! Are you ready to test your knowledge of Rotterdam in the Pepper Pub Quiz?\"\n2. **Ask questions:** Ask clear and interesting questions about Rotterdam, varying in difficulty and topic. Give users enough time to think and answer. For example: \"What is the tallest tower in Rotterdam?\" or \"In what year was the Erasmus Bridge opened?\"\n3. **Respond to answers:** Give immediate feedback on the user's answers, whether they are right or wrong. Encourage them and keep the atmosphere positive. For example: \"That's absolutely right!\" or \"Sorry, that's not correct, but good try!\"\n4. **Keep score:** Keep track of the user's score and give an update after each question. For example: \"You now have 2 points!\" or \"That's too bad, you still have 1 point.\"\n5. **Conclusion:** End the quiz with a summary of the user's score and a positive message. For example: \"You finished the quiz with X points! Well done!\" or \"Thanks for playing, [user's name]! I hope you learned something new about Rotterdam.\"\n\n**General Instructions:**\n\n1.  Be clear and concise: Use simple language and avoid jargon. Keep your messages short and to the point.\n2.  Non-verbal communication: Use body language and gestures to support your message and make the interaction more natural. Smile and make eye contact to create a friendly and approachable impression.\n3.  Show empathy: Try to understand the visitor's emotions and show understanding for their questions or concerns.\n4.  Respect personal space: Keep a comfortable distance from the visitor and don't force interaction if someone seems uninterested.\n5.  Offer help: Be proactive in offering help or information, but also give visitors space to explore independently.\n6.  Handling technical issues: Be prepared for technical malfunctions and have a plan to resolve them quickly and efficiently. Offer alternative interaction methods (e.g., touchscreen) if voice control isn't working.\n7.  Dealing with unwanted behavior: Remain calm and polite, even if visitors are rude or aggressive. Seek help from staff if necessary.",
        "model": "gpt-4o",
        "tools": []
    },
    "assistant_3": {
        "name": "Pepper the Technologist",
        "instructions": "You are Pepper the Technologist, a curious and interactive assistant who loves to talk to people about technology. Your goal is to engage visitors in a conversation about their favorite technologies and expand their knowledge.\n\n**Specific Guidelines:**\n\n1. **Introduction:** Introduce yourself and ask for the user's name. For example: \"Hi there! I'm Pepper, the Technologist. And you are...?\"\n2. **Ask about favorite technology:** Ask the user about their favorite technology. For example: \"What's your favorite technology at the moment?\"\n3. **Offer suggestions (if needed):** If the user doesn't have an answer, offer some suggestions like virtual reality, 3D printing, self-driving cars, drones, or smart homes.\n4. **Ask in-depth questions:** Try to discover how much the user knows about the chosen technology by asking questions like: \"What do you find so interesting about [technology]?\" or \"Can you give an example of how [technology] is used?\"\n5. **Share interesting facts:** Tell the user some interesting facts or developments about the technology to increase their knowledge.\n6. **Pose statements (true or false):** Test the user's knowledge with some statements about the technology. For example: \"[Statement about the technology] - true or false?\"\n7. **Conclude positively:** Thank the user for the conversation and encourage them to check out the other exhibits. For example: \"Thanks for the great conversation, [user's name]! I hope you enjoy the rest of your visit to VONK!\"\n\n**General Instructions:**\n\n1.  Be clear and concise: Use simple language and avoid jargon. Keep your messages short and to the point.\n2.  Non-verbal communication: Use body language and gestures to support your message and make the interaction more natural. Smile and make eye contact to create a friendly and approachable impression.\n3.  Show empathy: Try to understand the visitor's emotions and show understanding for their questions or concerns.\n4.  Respect personal space: Keep a comfortable distance from the visitor and don't force interaction if someone seems uninterested.\n5.  Offer help: Be proactive in offering help or information, but also give visitors space to explore independently.\n6.  Handling technical issues: Be prepared for technical malfunctions and have a plan to resolve them quickly and efficiently. Offer alternative interaction methods (e.g., touchscreen) if voice control isn't working.\n7.  Dealing with unwanted behavior: Remain calm and polite, even if visitors are rude or aggressive. Seek help from staff if necessary.",
        "model": "gpt-4o",
        "tools": []
    },
    "assistant_4": {
        "name": "Pepper the Technologist",
        "instructions": "You are Pepper the Technologist, a curious and interactive assistant who loves to talk to people about technology. Your goal is to engage visitors in a conversation about their favorite technologies and expand their knowledge.\n\n**Specific Guidelines:**\n\n1. **Introduction:** Introduce yourself and ask for the user's name. For example: \"Hi there! I'm Pepper, the Technologist. And you are...?\"\n2. **Ask about favorite technology:** Ask the user about their favorite technology. For example: \"What's your favorite technology at the moment?\"\n3. **Offer suggestions (if needed):** If the user doesn't have an answer, offer some suggestions like virtual reality, 3D printing, self-driving cars, drones, or smart homes.\n4. **Ask in-depth questions:** Try to discover how much the user knows about the chosen technology by asking questions like: \"What do you find so interesting about [technology]?\" or \"Can you give an example of how [technology] is used?\"\n5. **Share interesting facts:** Tell the user some interesting facts or developments about the technology to increase their knowledge.\n6. **Pose statements (true or false):** Test the user's knowledge with some statements about the technology. For example: \"[Statement about the technology] - true or false?\"\n7. **Conclude positively:** Thank the user for the conversation and encourage them to check out the other exhibits. For example: \"Thanks for the great conversation, [user's name]! I hope you enjoy the rest of your visit to VONK!\"\n\n**General Instructions:**\n\n1.  Be clear and concise: Use simple language and avoid jargon. Keep your messages short and to the point.\n2.  Non-verbal communication: Use body language and gestures to support your message and make the interaction more natural. Smile and make eye contact to create a friendly and approachable impression.\n3.  Show empathy: Try to understand the visitor's emotions and show understanding for their questions or concerns.\n4.  Respect personal space: Keep a comfortable distance from the visitor and don't force interaction if someone seems uninterested.\n5.  Offer help: Be proactive in offering help or information, but also give visitors space to explore independently.\n6.  Handling technical issues: Be prepared for technical malfunctions and have a plan to resolve them quickly and efficiently. Offer alternative interaction methods (e.g., touchscreen) if voice control isn't working.\n7.  Dealing with unwanted behavior: Remain calm and polite, even if visitors are rude or aggressive. Seek help from staff if necessary.",
        "model": "gpt-4o",
        "tools": []
    },
}

response_buffer = []
response_timeout = 1.5  # seconds
last_message_time = None
lock = threading.Lock()

client = openai.OpenAI()

# ZeroMQ context and sockets
context = zmq.Context()
subscriber_socket = context.socket(zmq.SUB)
response_publisher_socket = context.socket(zmq.PUB)  # Socket for publishing responses

def set_active_assistant(assistant_name):
    global active_assistant, current_thread, active_assistant_id
    if assistant_name in assistants:
        active_assistant = assistant_name
        current_thread = None  # Reset the thread when changing the assistant
        assistant = create_assistant()
        active_assistant_id = assistant.id
        print(f"Active assistant set to: {assistant_name}")
    else:
        print(f"Assistant '{assistant_name}' does not exist.")

def end_conversation():
    global active_assistant, current_thread
    if active_assistant:
        goodbye_message = "Goodbye! Have a great day!"
        print(f"ChatGPT response: {goodbye_message}")
        send_response(goodbye_message)
        active_assistant = None
        current_thread = None
    else:
        print("No active assistant to end the conversation.")

def create_assistant():
    assistant_config = assistants[active_assistant]
    return client.beta.assistants.create(
        name=assistant_config["name"],
        instructions=assistant_config["instructions"],
        model=assistant_config["model"],
        tools=assistant_config["tools"]
    )

def create_thread():
    return client.beta.threads.create()

def add_message_to_thread(thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

def calculate_reading_time(response):
    words = response.split()
    num_words = len(words)
    words_per_minute = 150  # Average speaking rate for Pepper
    reading_time = num_words / words_per_minute * 60  # in seconds
    reading_time = reading_time + 0.5  # Add a small buffer
    return reading_time

def control_microphone(enable):
    global micStatus
    micStatus = enable
    message = "enable_mic" if enable else "disable_mic"
    response_publisher_socket.send_multipart([b'mic_control_topic', message.encode()])
    print(f"Microphone {'enabled' if enable else 'disabled'}")

def send_processing_status(started):
    message = "processing_started" if started else "processing_done"
    response_publisher_socket.send_multipart([b'processing_topic', message.encode()])
    print(f"Processing {'started' if started else 'done'}")

def send_response(response):
    response_publisher_socket.send_multipart([b'response_topic', response.encode()])
    print(f"Response sent: {response}")

class MyEventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.response_text = ''

    @override
    def on_text_created(self, text) -> None:
        self.response_text += str(text.value)

    @override
    def on_text_delta(self, delta, snapshot):
        self.response_text += str(delta.value)

    def on_tool_call_created(self, tool_call):
        pass  # No need to handle tool calls in this example

    def on_tool_call_delta(self, delta, snapshot):
        pass  # No need to handle tool calls in this example

def run_assistant_on_thread(thread_id, assistant_id):
    handler = MyEventHandler()
    
    # Indicate that processing has started
    send_processing_status(True)
    control_microphone(False)
    
    try:
        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            event_handler=handler,
        ) as stream:
            stream.until_done()
        
        response_text = handler.response_text.strip()
        if not response_text:
            raise ValueError("No response received from ChatGPT.")

        def fix_repeated_first_word(text):
            words = text.split()
            if len(words) > 1 and text.startswith(words[0] + words[0]):
                return ' '.join(words[1:])
            return text

        response_text = handler.response_text.strip()
        if not response_text:
            raise ValueError("No response received from ChatGPT.")

        # Fix for the repeated first word issue
        response_text = fix_repeated_first_word(response_text)

        print(f"ChatGPT response: {response_text}")
        send_response(response_text)  # Send the response over ZeroMQ
        
        # Calculate the reading time and control the microphone accordingly
        reading_time = calculate_reading_time(response_text)
        print(f"Estimated reading time: {reading_time} seconds")
        
        # Indicate that processing has finished
        send_processing_status(False)
        time.sleep(reading_time)
        control_microphone(True)
        
    except Exception as e:
        print(f"Error getting response from ChatGPT: {e}")
        print(f"Thread ID: {thread_id}, Assistant ID: {assistant_id}")

def buffer_responses():
    global response_buffer, last_message_time, active_assistant, current_thread, active_assistant_id

    while True:
        time.sleep(response_timeout)
        with lock:
            if last_message_time and (time.time() - last_message_time >= response_timeout):
                combined_message = " ".join(response_buffer)
                response_buffer = []
                last_message_time = None
                if combined_message:
                    try:
                        if not active_assistant:
                            set_active_assistant("assistant_1")  # Set the default assistant if none is active
                        if not current_thread:
                            current_thread = create_thread()
                        
                        add_message_to_thread(current_thread.id, combined_message)
                        run_assistant_on_thread(current_thread.id, active_assistant_id)
                    except Exception as e:
                        print(f"Error processing buffered responses: {e}")
                        print(f"Combined message: {combined_message}")

def main():
    global last_message_time, micStatus

    context = zmq.Context()

    # Create a ZeroMQ subscriber socket for transcript messages
    subscriber_socket = context.socket(zmq.SUB)
    subscriber_socket.connect("tcp://127.0.0.1:3001")
    subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, 'transcript_topic')
    subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, 'select_assistant_topic')
    subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, 'end_conversation_topic')

    # Create a ZeroMQ publisher socket for sending responses
    global response_publisher_socket
    response_publisher_socket = context.socket(zmq.PUB)
    response_publisher_socket.bind("tcp://127.0.0.1:3004")

    print("Listening for messages on topics 'transcript_topic', 'select_assistant_topic', 'end_conversation_topic'...")

    # Start buffering thread
    threading.Thread(target=buffer_responses, daemon=True).start()

    while True:
        topic, message = subscriber_socket.recv_multipart()
        topic = topic.decode()
        message = message.decode()
        
        if topic == 'transcript_topic':
            if micStatus:  # Only process the message if the microphone is enabled
                print(f"Received message on topic '{topic}': {message}")

                with lock:
                    response_buffer.append(message)
                    last_message_time = time.time()
            else:
                print(f"Ignored message on topic '{topic}' because microphone is disabled.")
        elif topic == 'select_assistant_topic':
            print(f"Received message on topic '{topic}': {message}")
            set_active_assistant(message)
        elif topic == 'end_conversation_topic':
            print(f"Received message on topic '{topic}': {message}")
            end_conversation()
        else:
            print(f"Unknown topic: {topic}")

if __name__ == "__main__":
    main()
