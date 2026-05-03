const fs = require('fs');
const path = require('path');

module.exports = function handler(req, res) {
  res.status(200).json({
    robot: { urdfPath: './assets/urdf', urdfFile: 'armpi_fpv.urdf', meshesPath: './assets/meshes' },
    display: { defaultLanguage: 'zh', cameraPosition: { x: -0.34, y: 0.25, z: -0.5 }, robotRotationX: -1.5707963267948966, robotPositionY: 0.02 }
  });
};
