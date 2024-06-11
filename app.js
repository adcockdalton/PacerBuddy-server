const express = require("express");
const { spawn } = require("child_process");

let pythonProcess;

const app = express();
app.use(express.json());

const PORT = 3000;

app.listen(PORT, () => {
  console.log("Server Listening on PORT:", PORT);
});

app.get("/status", (request, response) => {
  const status = {
    Status: "Running",
  };

  response.send(status);
});

app.post("/startrover", (request, response) => {
  const { pace } = request.body;
  console.log("pace", pace);
  runPythonScript("Rover/index.py", [pace]);

  const res = {
    Rover: "on",
  };

  response.send(res);
});

app.post("/killrover", (request, response) => {
  if (pythonProcess) {
    pythonProcess.kill("SIGINT");
  }

  const res = {
    Rover: "off",
  };

  response.send(res);
});

// Function to run a Python script asynchronously
function runPythonScript(scriptPath, args) {
  pythonProcess = spawn("python", [scriptPath].concat(args));

  // Handle standard output
  pythonProcess.stdout.on("data", (stdout) => {
    console.log(`stdout: ${stdout.toString()}`);
  });

  // Handle standard error
  pythonProcess.stderr.on("data", (stderr) => {
    console.error(`stderr: ${stderr.toString()}`);
  });

  // Handle process exit
  pythonProcess.on("close", (code) => {
    console.log(`child process exited with code ${code}`);
  });
}
