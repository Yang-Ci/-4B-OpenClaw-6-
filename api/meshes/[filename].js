const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  const filename = req.query.filename || '';
  const filePath = path.join(process.cwd(), 'web-simulator', 'assets', 'meshes', filename);
  try {
    const data = fs.readFileSync(filePath);
    res.setHeader('Content-Type', 'model/stl');
    res.status(200).send(data);
  } catch(e) {
    res.status(404).json({ error: 'not found: ' + filename });
  }
}
