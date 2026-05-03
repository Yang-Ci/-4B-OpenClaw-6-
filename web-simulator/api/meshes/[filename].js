const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  const filename = req.query.filename || '';
  const configPath = path.join(process.cwd(), 'config.json');
  let config = { robot: { meshesPath: './assets/meshes' } };
  try {
    if (fs.existsSync(configPath)) {
      config = { ...config, ...JSON.parse(fs.readFileSync(configPath, 'utf8')) };
    }
  } catch(e) {}
  const filePath = path.join(process.cwd(), config.robot.meshesPath, filename);
  try {
    const data = fs.readFileSync(filePath);
    res.setHeader('Content-Type', 'model/stl');
    res.status(200).send(data);
  } catch(e) {
    res.status(404).json({ error: 'not found: ' + filename });
  }
}
