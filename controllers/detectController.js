const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

exports.processImage = (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No image uploaded" });
    }

    // Save the uploaded file in `/tmp/` (temporary directory)
    const imagePath = `/tmp/${Date.now()}_${req.file.originalname}`;
    fs.writeFileSync(imagePath, req.file.buffer);
    console.log("Image saved at:", imagePath);

    //  Output path (You might not need this for detection)
    const outputPath = `/tmp/detected_output.jpg`;

    //  Run the Python script with the correct file path
    const pythonProcess = spawn("python3", ["ai/detect.py", imagePath]);

    let result = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
        const text = data.toString().trim();
        console.log("Detected Output:", text);  

        // Store only valid JSON lines
        if (text.startsWith("{") || text.startsWith("[")) {
            result += text;
            console.log("Result:", result);
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

            // ✅ Return image URL pointing to `/tmp/`
            res.json({ 
                parseResult,
                imageUrl: `http://localhost:5000/tmp/detected_output.jpg` 
            });
             
        } catch (error) {
            console.error("JSON Parsing Error:", error.message);
            res.status(500).json({ error: "Error processing image", details: result });
        }
    });
};
