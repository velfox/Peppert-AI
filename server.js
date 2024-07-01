const express = require("express");
const http = require("http");
const { createClient } = require("@deepgram/sdk");
const dotenv = require("dotenv");
const zmq = require("zeromq");
const { Server } = require("socket.io");

dotenv.config();

const client = createClient(process.env.DEEPGRAM_API_KEY);
const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Create a ZeroMQ publisher and subscriber socket
const pubSock = new zmq.Publisher();
const subSock = new zmq.Subscriber();

async function startZeroMQ() {
  await pubSock.bind('tcp://127.0.0.1:3001');
  await subSock.connect('tcp://127.0.0.1:3004');
  subSock.subscribe('mic_control_topic');
  subSock.subscribe('processing_topic');
  subSock.subscribe('response_topic');
  console.log('ZeroMQ publisher bound to port 3001 and subscriber connected to port 3002');

  for await (const [topic, msg] of subSock) {
    const message = msg.toString();
    console.log(`Received message on topic '${topic.toString()}': ${message}`);
    io.emit(topic.toString(), message); // Forward the message to the client via Socket.io
  }
}

// Start ZeroMQ
startZeroMQ();

app.use(express.static("public/"));
app.use(express.json());

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public/index.html");
});

const getProjectId = async () => {
  const { result, error } = await client.manage.getProjects();

  if (error) {
    throw error;
  }

  return result.projects[0].project_id;
};

const getTempApiKey = async (projectId) => {
  const { result, error } = await client.manage.createProjectKey(projectId, {
    comment: "short lived",
    scopes: ["usage:write"],
    time_to_live_in_seconds: 20,
  });

  if (error) {
    throw error;
  }

  return result;
};

app.get("/key", async (req, res) => {
  const projectId = await getProjectId();
  const key = await getTempApiKey(projectId);

  res.json(key);
});

app.post("/transcript", (req, res) => {
  const transcript = req.body.transcript;
  if (transcript) {
    // Publish the transcript to ZeroMQ
    pubSock.send(['transcript_topic', transcript]);
    res.status(200).send('Transcript received and sent to ZeroMQ');
  } else {
    res.status(400).send('No transcript provided');
  }
});

// Handle Socket.io events from the client and send messages over ZeroMQ
io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('user_detected', () => {
    console.log('User detected');
    pubSock.send(['user_detected_topic', 'User detected']);
  });

  socket.on('tablet_webpage_started', () => {
    console.log('Tablet webpage started');
    pubSock.send(['tablet_webpage_started_topic', 'Tablet webpage started']);
  });

  socket.on('select_assistant', (assistant) => {
    console.log(`Assistant selected: ${assistant}`);
    pubSock.send(['select_assistant_topic', `${assistant}`]);
  });

  socket.on('end_conversation', () => {
    console.log('End conversation');
    pubSock.send(['end_conversation_topic', 'End conversation']);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

server.listen(3000, () => {
  console.log("listening on http://localhost:3000");
});
