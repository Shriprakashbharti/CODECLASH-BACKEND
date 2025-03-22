const express = require("express");
const upload = require("../middleware/uploadMiddleware");
const { processImage } = require("../controllers/detectController");

const router = express.Router();

// API: Upload Image & Detect Objects
router.post("/upload", upload.single("image"), processImage);

module.exports = router;
