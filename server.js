require("dotenv").config();
const express = require("express");
const cors = require("cors");
const detectRoutes = require("./routes/detectRoutes");
const path = require("path");
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// app.use("/uploads", express.static(path.join(__dirname, "uploads")));
app.use(express.urlencoded({ extended: true }));


app.use((req, res, next) => {
    console.log(`🔗 ${req.method} ${req.url}`);
    next();
});

// Routes
app.use("/api/detect", detectRoutes);

// Start Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on http://localhost:${PORT}`));
