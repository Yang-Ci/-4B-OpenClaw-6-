const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  const configPath = path.join(process.cwd(), 'config.json');
  let config = {
    robot: { urdfPath: './assets/urdf', urdfFile: 'armpi_fpv.urdf', meshesPath: './assets/meshes' },
    display: { defaultLanguage: 'zh' }
  };
  try {
    if (fs.existsSync(configPath)) {
      config = { ...config, ...JSON.parse(fs.readFileSync(configPath, 'utf8')) };
    }
  } catch(e) {}
  res.status(200).json({ robot: config.robot, display: config.display || {} });
}
