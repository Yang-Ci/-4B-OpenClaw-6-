module.exports = function handler(req, res) {
  res.status(200).json([
    { name: 'joint1', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (base)' },
    { name: 'joint2', min: -1.57, max: 1.57, current: 0, axis: 'X-rotation (shoulder)' },
    { name: 'joint3', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (elbow)' },
    { name: 'joint4', min: -2.09, max: 2.09, current: 0, axis: 'X-rotation (wrist1)' },
    { name: 'joint5', min: -2.09, max: 2.09, current: 0, axis: 'Z-rotation (wrist2)' },
    { name: 'r_joint', min: -1.57, max: 1.57, current: 0, axis: 'Gripper open/close' }
  ]);
};
