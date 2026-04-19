const express = require("express");
const multer = require("multer");
const cors = require("cors");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// Multer: store uploaded images in uploads/
const upload = multer({
  dest: path.join(__dirname, "uploads"),
  limits: { fileSize: 20 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith("image/")) cb(null, true);
    else cb(new Error("Only image files allowed"));
  },
});

if (!fs.existsSync(path.join(__dirname, "uploads"))) {
  fs.mkdirSync(path.join(__dirname, "uploads"));
}

// ──────────────────────────────────────────────
// POST /api/analyze  — core analysis endpoint
// ──────────────────────────────────────────────
app.post("/api/analyze", upload.single("image"), (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No image uploaded" });

  const imagePath = req.file.path;

  // Call Python analyze.py with the image path
  const python = spawn("python", [
    path.join(__dirname, "analyze.py"),
    imagePath,
  ]);

  let output = "";
  let errorOutput = "";

  python.stdout.on("data", (data) => (output += data.toString()));
  python.stderr.on("data", (data) => (errorOutput += data.toString()));

  python.on("close", (code) => {
    // Clean up uploaded file
    fs.unlink(imagePath, () => {});

    if (code !== 0) {
      console.error("Python error:", errorOutput);
      return res.status(500).json({
        error: "Analysis failed",
        details: errorOutput.slice(-300),
      });
    }

    try {
      const result = JSON.parse(output.trim());
      return res.json(result);
    } catch (e) {
      console.error("JSON parse error:", output);
      return res.status(500).json({ error: "Invalid response from AI engine" });
    }
  });
});

// ──────────────────────────────────────────────
// GET /api/monuments — return monument database
// ──────────────────────────────────────────────
app.get("/api/monuments", (req, res) => {
  try {
    const db = JSON.parse(
      fs.readFileSync(path.join(__dirname, "requirements.json"), "utf8")
    );
    res.json(db);
  } catch {
    res.status(500).json({ error: "Could not load monument database" });
  }
});

// ──────────────────────────────────────────────
// GET /api/health
// ──────────────────────────────────────────────
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

app.listen(PORT, () =>
  console.log(`✅  Vishwakarma AI backend running on http://localhost:${PORT}`)
);
