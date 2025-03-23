const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

exports.processImage = (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No image uploaded" });
    }

    // Define paths
    const uploadsDir = path.join(__dirname, "..", "uploads");
    if (!fs.existsSync(uploadsDir)) {
        fs.mkdirSync(uploadsDir, { recursive: true });
    }

    const imagePath = path.join(uploadsDir, `${Date.now()}_${req.file.originalname}`);
    fs.writeFileSync(imagePath, req.file.buffer);
    console.log("✅ Image saved at:", imagePath);

    const pythonScriptPath = path.join(__dirname, "..", "ai", "detect.py");
    console.log("📌 Running Python script:", pythonScriptPath);

    // Spawn the Python process
    const pythonProcess = spawn("python3", [pythonScriptPath, imagePath]);

    let result = "";
    let errorOutput = "";

    pythonProcess.stdout.on("data", (data) => {
        const text = data.toString().trim();
        console.log("🔍 Detected Output:", text);
        if (text.startsWith("{") || text.startsWith("[")) {
            result += text;
        }
    });

    pythonProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
        console.error("⚠️ Python Error:", errorOutput);
    });

    pythonProcess.on("close", (code) => {
        console.log(`🚀 Python process exited with code ${code}`);

        if (errorOutput) {
            return res.status(500).json({ error: "Python script error", details: errorOutput });
        }

        try {
            if (!result.trim().startsWith("{") && !result.trim().startsWith("[")) {
                throw new Error("Invalid JSON output from Python");
            }
            const parseResult = JSON.parse(result);

            res.json({ 
                parseResult, 
                imageUrl: `https://object-detection-tbc1.onrender.com/uploads/detected_output.jpg`
            });
        } catch (error) {
            console.error("❌ JSON Parsing Error:", error.message);
            res.status(500).json({ error: "Error processing image", details: result });
        }
    });
};
