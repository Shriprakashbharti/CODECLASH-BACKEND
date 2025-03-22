
const { spawn } = require("child_process");

const pythonProcess = spawn("python", ["-c", "print('Hello from Python!')"]);

pythonProcess.stdout.on("data", (data) => {
    console.log(`Python Output: ${data}`);
});

pythonProcess.stderr.on("data", (data) => {
    console.error(`Python Error: ${data}`);
});
