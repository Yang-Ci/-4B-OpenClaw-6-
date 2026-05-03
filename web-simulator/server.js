const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();

const configPath = path.join(__dirname, 'config.json');
let config = {
  server: { port: 3000, host: 'localhost' },
  robot: {
    urdfPath: './assets/urdf',
    urdfFile: 'armpi_fpv.urdf',
    meshesPath: './assets/meshes'
  },
  display: { defaultLanguage: 'zh' }
};

try {
  if (fs.existsSync(configPath)) {
    const configFile = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    config = { ...config, ...configFile };
  }
} catch (err) {}

app.use(cors());
app.use(express.json());

function loadFile(filePath) {
  try {
    return fs.readFileSync(path.join(__dirname, filePath));
  } catch (e) {
    return null;
  }
}

const indexHtml = loadFile('public/index.html');
const faviconPng = loadFile('public/favicon.png');
const mainJs = loadFile('public/js/main.js');
const stlLoaderJs = loadFile('public/lib/STLLoader.js');
const stlLoaderUmdJs = loadFile('public/lib/STLLoader-umd.js');
const threeMinJs = loadFile('public/lib/three.min.js');
const threeR128MinJs = loadFile('public/lib/three-r128.min.js');

const urdfContent = loadFile(path.join(config.robot.urdfPath, config.robot.urdfFile));

const meshDir = path.join(__dirname, config.robot.meshesPath);
const meshFiles = {};
if (fs.existsSync(meshDir)) {
  fs.readdirSync(meshDir).forEach(f => {
    meshFiles[f] = fs.readFileSync(path.join(meshDir, f));
  });
}

app.get('/', (req, res) => {
  if (!indexHtml) return res.status(500).send('index.html not found');
  res.type('html').send(indexHtml);
});

app.get('/index.html', (req, res) => {
  if (!indexHtml) return res.status(500).send('index.html not found');
  res.type('html').send(indexHtml);
});

app.get('/favicon.png', (req, res) => {
  if (!faviconPng) return res.status(404).send('');
  res.type('image/png').send(faviconPng);
});

app.get('/js/main.js', (req, res) => {
  if (!mainJs) return res.status(404).send('');
  res.type('application/javascript').send(mainJs);
});

app.get('/lib/STLLoader.js', (req, res) => {
  if (!stlLoaderJs) return res.status(404).send('');
  res.type('application/javascript').send(stlLoaderJs);
});

app.get('/lib/STLLoader-umd.js', (req, res) => {
  if (!stlLoaderUmdJs) return res.status(404).send('');
  res.type('application/javascript').send(stlLoaderUmdJs);
});

app.get('/lib/three.min.js', (req, res) => {
  if (!threeMinJs) return res.status(404).send('');
  res.type('application/javascript').send(threeMinJs);
});

app.get('/lib/three-r128.min.js', (req, res) => {
  if (!threeR128MinJs) return res.status(404).send('');
  res.type('application/javascript').send(threeR128MinJs);
});

app.get('/api/config', (req, res) => {
  res.json({ robot: config.robot, display: config.display || {} });
});

app.get('/api/urdf', (req, res) => {
  if (!urdfContent) return res.status(500).json({ error: 'URDF file not found' });
  res.type('application/xml').send(urdfContent);
});

app.get('/api/meshes/:filename', (req, res) => {
  const data = meshFiles[req.params.filename];
  if (!data) return res.status(404).json({ error: `File not found: ${req.params.filename}` });
  res.type('model/stl').send(data);
});

app.get('/api/armpi_fpv_description/meshes/:filename', (req, res) => {
  const data = meshFiles[req.params.filename];
  if (!data) return res.status(404).json({ error: `File not found: ${req.params.filename}` });
  res.type('model/stl').send(data);
});

app.get('/api/joints', (req, res) => {
  res.json([
    { name: 'joint1', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (base)' },
    { name: 'joint2', min: -1.57, max: 1.57, current: 0, axis: 'X-rotation (shoulder)' },
    { name: 'joint3', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (elbow)' },
    { name: 'joint4', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (wrist1)' },
    { name: 'joint5', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (wrist2)' },
    { name: 'r_joint', min: -1.57, max: 1.57, current: 0, axis: 'Gripper open/close' }
  ]);
});

app.use((req, res) => {
  if (!indexHtml) return res.status(500).send('index.html not found');
  res.type('html').send(indexHtml);
});

module.exports = app;
