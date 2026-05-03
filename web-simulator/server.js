const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();

const configPath = path.join(__dirname, 'config.json');
let config = {
  server: { port: 3000, host: 'localhost' },
  robot: {
    urdfPath: '../src/armpi_fpv_descrption',
    urdfFile: 'urdf/armpi_fpv.urdf',
    meshesPath: 'meshes'
  }
};

try {
  if (fs.existsSync(configPath)) {
    const configFile = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    config = { ...config, ...configFile };
    console.log('✓ Config loaded from config.json');
  }
} catch (err) {
  console.log('⚠ Using default config (config.json not found or invalid)');
}

const PORT = process.env.PORT || config.server.port;

app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, 'public'), {
  etag: false,
  setHeaders: (res, path) => {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
  }
}));

app.use('/modules', express.static(path.join(__dirname, 'node_modules')));

app.get('/api/config', (req, res) => {
  res.json({
    robot: config.robot,
    display: config.display || {}
  });
});

const urdfPath = path.resolve(path.join(__dirname, config.robot.urdfPath));
const urdfFile = path.join(urdfPath, config.robot.urdfFile);
const meshesPath = path.join(urdfPath, config.robot.meshesPath);

console.log('\n📁 URDF Path:', urdfPath);
console.log('📄 URDF File:', urdfFile);
console.log('🎨 Meshes Path:', meshesPath);

app.get('/api/urdf', (req, res) => {
  try {
    let urdfContent = fs.readFileSync(urdfFile, 'utf8');
    res.type('application/xml').send(urdfContent);
  } catch (err) {
    res.status(500).json({ error: 'Failed to read URDF file', details: err.message });
  }
});

app.get('/api/meshes/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(meshesPath, filename);

  if (fs.existsSync(filePath)) {
    res.sendFile(filePath);
  } else {
    res.status(404).json({ error: `File not found: ${filename}` });
  }
});

app.get('/api/armpi_fpv_description/meshes/:filename', (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join(meshesPath, filename);

  if (fs.existsSync(filePath)) {
    res.sendFile(filePath);
  } else {
    res.status(404).json({ error: `File not found: ${filename}` });
  }
});

app.get('/api/joints', (req, res) => {
  const joints = [
    { name: 'joint1', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (base)' },
    { name: 'joint2', min: -1.57, max: 1.57, current: 0, axis: 'X-rotation (shoulder)' },
    { name: 'joint3', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (elbow)' },
    { name: 'joint4', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (wrist1)' },
    { name: 'joint5', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (wrist2)' },
    { name: 'r_joint', min: -1.57, max: 1.57, current: 0, axis: 'Gripper open/close' }
  ];
  res.json(joints);
});

app.listen(PORT, () => {
  console.log('\n========================================');
  console.log('  ArmPi Pro Robot Simulator Started!');
  console.log('========================================');
  console.log(`  Local:   http://localhost:${PORT}`);
  console.log(`  URDF:    http://localhost:${PORT}/api/urdf`);
  console.log(`  Config:  http://localhost:${PORT}/api/config`);
  console.log('----------------------------------------');
  console.log(`  Port: ${PORT} (change with PORT env var)`);
  console.log('  Press CTRL+C to stop the server\n');
});
