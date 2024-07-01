const socket = io(); // Ensure Socket.io is initialized here

let micStatus = true;
let mediaStream;
let microphone;

function showScreen(screenId) {
    console.log("Showing screen: ", screenId);
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => screen.classList.add('hidden'));
    screens.forEach(screen => screen.classList.remove('active'));
    document.getElementById(screenId).classList.remove('hidden');
    document.getElementById(screenId).classList.add('active');
}

async function getMicrophone() {
    const userMedia = await navigator.mediaDevices.getUserMedia({
        audio: true,
    });
    mediaStream = userMedia; // Store mediaStream for muting/unmuting
    return new MediaRecorder(userMedia);
}

async function openMicrophone(microphone, socket) {
    await microphone.start(500);

    microphone.onstart = () => {
        console.log("client: microphone opened");
        document.body.classList.add("recording");
        startListening();
        muteMicrophone();
    };

    microphone.onstop = () => {
        console.log("client: microphone closed");
        document.body.classList.remove("recording");
        resetAnimation();
    };

    microphone.ondataavailable = (e) => {
        const data = e.data;
        console.log("client: sent data to websocket");
        socket.send(data);
    };
}

async function closeMicrophone(microphone) {
    microphone.stop();
}

function muteMicrophone() {
    if (mediaStream) {
        mediaStream.getAudioTracks()[0].enabled = false;
        console.log("Microphone muted.");
    }
}

function unmuteMicrophone() {
    if (mediaStream) {
        mediaStream.getAudioTracks()[0].enabled = true;
        console.log("Microphone unmuted.");
        startListening();
    }
}

async function start(socket) {
    console.log("client: waiting to open microphone");

    if (!microphone) {
        // open and close the microphone
        microphone = await getMicrophone();
        await openMicrophone(microphone, socket);
    } else {
        await closeMicrophone(microphone);
        microphone = undefined;
    }
}

async function getTempApiKey() {
    const result = await fetch("/key");
    const json = await result.json();

    return json.key;
}

async function handleMicControlMessage(message) {
    console.log(`Received mic control message: ${message}`);
    if (message === "enable_mic") {
        console.log("Enabling microphone ZQM function");
        document.body.classList.add("recording");
        micStatus = true;
        unmuteMicrophone(); // Unmute the microphone
    } else if (message === "disable_mic") {
        console.log("Disabling microphone ZQM function");
        document.body.classList.remove("recording");
        micStatus = false;
        muteMicrophone(); // Mute the microphone
    }
}

function handleProcessingStatusMessage(message) {
    if (message === "processing_started") {
        console.log("Processing started");
        startProcessing();
    } else if (message === "processing_done") {
        console.log("Processing done");
    }
}

function handleChatGptResponse(message) {
    console.log(`ChatGPT response: ${message}`);
    updateTextContainer(message);
    startResponding();
}

window.addEventListener("load", async () => {
    const key = await getTempApiKey();

    const { createClient } = deepgram;
    const _deepgram = createClient(key);

    const deepgramSocket = _deepgram.listen.live({ model: "nova", smart_format: true });

    deepgramSocket.on("open", async () => {
        console.log("client: connected to Deepgram websocket");

        deepgramSocket.on("Results", async (data) => {
            console.log(data);

            const transcript = data.channel.alternatives[0].transcript;

            if (transcript !== "" && micStatus === true) {
                console.log("Transcript MICSTATE: ", micStatus + " Micstatus " + transcript);
                // Send the transcript to the server
                await fetch("/transcript", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ transcript: transcript }),
                });
                updateTextContainer(transcript); // Update the text container with transcript
            }
        });

        deepgramSocket.on("error", (e) => console.error(e));

        deepgramSocket.on("warning", (e) => console.warn(e));

        deepgramSocket.on("Metadata", (e) => console.log(e));

        deepgramSocket.on("close", (e) => console.log(e));

        await start(deepgramSocket);
    });

    // Setup Socket.io client to listen to server messages and log everything
    socket.onAny((event, ...args) => {
        console.log(`Received event: ${event}, with args: ${JSON.stringify(args)}`);
    });

    socket.on('mic_control_topic', handleMicControlMessage);
    socket.on('processing_topic', handleProcessingStatusMessage);
    socket.on('response_topic', handleChatGptResponse);
});

// Functions to control animations and text container
function startListening() {
    const logo = document.getElementById('logo');
    logo.classList.remove('responding', 'processing');
    logo.classList.add('listening');
}

function startResponding() {
    const logo = document.getElementById('logo');
    logo.classList.remove('listening', 'processing');
    logo.classList.add('responding');
}

function startProcessing() {
    const logo = document.getElementById('logo');
    logo.classList.remove('listening', 'responding');
    logo.classList.add('processing');
}

function resetAnimation() {
    const logo = document.getElementById('logo');
    logo.classList.remove('listening', 'responding', 'processing');
}

function updateTextContainer(text) {
    const textContainer = document.getElementById('text-container');
    const textOutput = document.getElementById('text-output');
    textContainer.style.opacity = 0;
    setTimeout(() => {
        textOutput.innerText = text;
        textContainer.classList.add('show');
        adjustFontSize();
        textContainer.style.opacity = 1;
    }, 500); // match this with the transition duration
}

function clearTextContainer() {
    const textContainer = document.getElementById('text-container');
    textContainer.style.opacity = 0;
    setTimeout(() => {
        const textOutput = document.getElementById('text-output');
        textOutput.innerText = "";
        textContainer.classList.remove('show');
    }, 500); // match this with the transition duration
}

function adjustFontSize() {
    const textOutput = document.getElementById('text-output');
    const textContainer = document.getElementById('text-container');
    const containerHeight = textContainer.clientHeight;
    const containerWidth = textContainer.clientWidth;
    let fontSize = parseInt(window.getComputedStyle(textOutput).fontSize);
    textOutput.style.fontSize = `${fontSize}px`;

    while (textOutput.scrollHeight > containerHeight || textOutput.scrollWidth > containerWidth) {
        fontSize--;
        textOutput.style.fontSize = `${fontSize}px`;
    }
}

function goBack() {
    showScreen('assistant-selection-screen');
}

function endConversation() {
  socket.emit('end_conversation');
  muteMicrophone();
  showScreen('goodbye-screen');
  setTimeout(() => {
      showScreen('welcome-screen');
  }, 5000); // Show the welcome screen after 5 seconds
}

function detectUser() {
    console.log("User detected");
    socket.emit('user_detected');
    showScreen('privacy-screen');
}

function startfull() {
    console.log("aplication started");
    socket.emit('tablet_webpage_started');
    showScreen('welcome-screen');
    muteMicrophone();
    enterFullScreen(document.documentElement);    
}

function acceptPrivacy() {
    showScreen('assistant-selection-screen');
}

function declinePrivacy() {
    muteMicrophone();
    showScreen('welcome-screen');
}

function selectAssistant(assistantId) {
    socket.emit('select_assistant', assistantId);
    updateTextContainer("Talk to me, to start the conversation.");
    showScreen('interaction-screen');
    unmuteMicrophone();
}

function enterFullScreen(element) {
    if(element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();     // Firefox
    } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();  // Safari
    } else if(element.msRequestFullscreen) {
        element.msRequestFullscreen();      // IE/Edge
    }
}
