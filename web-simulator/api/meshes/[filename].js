const fs = require('fs');
const path = require('path');

module.exports = function handler(req, res) {
  const filename = req.query.filename || '';
  const candidates = [
    path.join(process.cwd(), 'public', 'assets', 'meshes', filename),
    path.join(process.cwd(), 'assets', 'meshes', filename)
  ];
  try {
    const filePath = candidates.find(file => fs.existsSync(file));
    if (!filePath) throw new Error('mesh not found');
    const data = fs.readFileSync(filePath);
    res.setHeader('Content-Type', 'model/stl');
    res.status(200).send(data);
  } catch(e) {
    res.status(404).json({ error: 'not found: ' + filename });
  }
};
