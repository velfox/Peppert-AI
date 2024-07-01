# AI Assistant System for Pepper

## Overview

This project is an AI-powered assistant system designed to run on Pepper the robot, as well as a standard computer for testing. The system uses Python scripts for various functionalities, a web interface for interaction, and ZeroMQ for communication between components.

Created By Tim - velfox.

## Features

* **AI-Powered Interactions:**  Leverages AI models (e.g., ChatGPT) for natural language understanding and responses.
* **Pepper Integration:**  Specific scripts for Pepper's hardware (text-to-speech, human tracking).
* **Web Interface:**  User-friendly interface for testing and interaction.
* **ZeroMQ Communication:**  Robust and efficient messaging between components.

## Project Structure

assistants/
├── assistants.json          # Configuration for AI assistants
node_modules/               # Node.js dependencies
Pepper_scripts/             # Scripts specific to the Pepper robot
    pepper_humen_tracker.py  # Human tracking script
    pepper_tts.py           # Text-to-speech script
public/
├── CMS_not_implemented/    # Placeholder for future content management
├── img/                    # Images used in the project
├── client.js               # Client-side JavaScript for the web app
├── index.html              # Main HTML file for the web app
└── style.css               # Styles for the web app
tests/                      # Scripts for testing the system
    openAI_audio_playback_test.py 
    testZmqMessages.py             
    ttsListener.py                 
.env                        # Environment variables (not in version control)
.gitignore                  # Files and folders to ignore in Git
package-lock.json           # Lockfile for npm dependencies
package.json                # Project metadata and dependencies for npm
server.js                   # Main Node.js server
zmqChatGpt.py               # Script for handling ChatGPT interaction

## Prerequisites

* **Node.js:** Download and install from [https://nodejs.org/](https://nodejs.org/)
* **Python 2 & 3:** Required for Pepper scripts (Python 2) and testing (Python 3)
* **Pepper SDK:**  Install the SDK for running Pepper scripts
* **Environment Variables:**
    * `DEEPGRAM_API_KEY`
    * `OPENAI_API_KEY` (Place these in a `.env` file)

## Setup

1. **Clone the Repository:** `git clone <repository-url>`
2. **Install Node.js Dependencies:** `npm install`
3. **Install Python Dependencies:**
    * **Python 2 (Pepper):** `pip2 install qi zeromq`
    * **Python 3 (Testing):** `pip3 install openai zeromq`

## Usage

1. **Start Web Server:** `npm start` (Access at http://localhost:3000)
2. **Run ChatGPT Script:** `python3 zmqChatGpt.py`
3. **Run Pepper Scripts (Optional):**
    * `python2 pepper_tts.py`

## Testing Without Pepper

Use the scripts in the `tests` directory with Python 3:

* `python3 ttsListener.py` (Example)

## Communication Flow

1. **Web Client:** User interacts, sends messages to the server via Socket.io.
2. **Server:** Forwards messages to ZeroMQ topics.
3. **Python Scripts:** Listen for ZeroMQ messages and perform actions.

## Contributing

Contributions are welcome! Please submit a pull request.

## License

This project is licensed under the MIT License.
