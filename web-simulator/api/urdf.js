const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  const configPath = path.join(process.cwd(), 'config.json');
  let config = { robot: { urdfPath: './assets/urdf', urdfFile: 'armpi_fpv.urdf' } };
  try {
    if (fs.existsSync(configPath)) {
      config = { ...config, ...JSON.parse(fs.readFileSync(configPath, 'utf8')) };
    }
  } catch(e) {}
  const urdfFile = path.join(process.cwd(), config.robot.urdfPath, config.robot.urdfFile);
  try {
    const content = fs.readFileSync(urdfFile, 'utf8');
    res.setHeader('Content-Type', 'application/xml');
    res.status(200).send(content);
  } catch(e) {
    res.status(500).json({ error: 'URDF not found', path: urdfFile });
  }
}
