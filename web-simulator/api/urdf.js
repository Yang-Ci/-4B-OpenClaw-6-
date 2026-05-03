const fs = require('fs');
const path = require('path');

module.exports = function handler(req, res) {
  const candidates = [
    path.join(process.cwd(), 'public', 'assets', 'urdf', 'armpi_fpv.urdf'),
    path.join(process.cwd(), 'assets', 'urdf', 'armpi_fpv.urdf')
  ];
  try {
    const urdfFile = candidates.find(file => fs.existsSync(file));
    if (!urdfFile) throw new Error('URDF not found');
    const content = fs.readFileSync(urdfFile, 'utf8');
    res.setHeader('Content-Type', 'application/xml');
    res.status(200).send(content);
  } catch(e) {
    res.status(500).json({ error: 'URDF not found', paths: candidates });
  }
};
