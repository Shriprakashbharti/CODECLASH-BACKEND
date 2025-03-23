const { spawn } = require("child_process");
const path = require("path");

exports.processImage = (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No image uploaded" });
    }

    const imagePath = path.join(__dirname, "../uploads", req.file.filename);
    const pythonPath = "C:\\Program Files\\Python310\\python.exe";  // Change this if needed
    const outputPath = path.join(__dirname, "../uploads/DetectedOutput/detected_output.jpg");
    const pythonProcess = spawn(pythonPath, ["ai/detect.py", imagePath]);

    let result = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
        const text = data.toString().trim();
        console.log("Detected Output:", text);  // Log for debugging

        // Only store valid JSON lines
        if (text.startsWith("{") || text.startsWith("[")) {
            result += text;
            console.log("Result : ",result);
        }
    });

    pythonProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
        console.error("Python Error:", errorOutput);
    });

    pythonProcess.on("close", (code) => {
        console.log(`Python process exited with code ${code}`);
        
        if (errorOutput) {
            return res.status(500).json({ error: "Python script error", details: errorOutput });
        }

        try {
            if (!result.trim().startsWith("{") && !result.trim().startsWith("[")) {
                throw new Error("Invalid JSON output from Python");
            }
            const parseResult = result.trim() ? JSON.parse(result) : [];
            console.log(parseResult);
            if (parseResult.length === 0) {
                console.log("No objects detected.");
            }
            res.json({ 
                parseResult,
                imageUrl:"http://localhost:4000/uploads/detected_output.jpg" 
             });
             
        } catch (error) {
            console.error("JSON Parsing Error:", error.message);
            res.status(500).json({ error: "Error processing image", details: result });
        }
    });
};

