let scene, camera, renderer, controls;
let robot = null;
let ghostRobot = null;
let isAnimating = false;
let animationTime = 0;
let isDragMode = false;
let isDraggingEndEffector = false;
let targetJointAngles = {};
let currentJointAngles = { joint1: 0, joint2: 5, joint3: 65, joint4: 30, joint5: 0, gripper: 0 };
let isMovingToTarget = false;
let moveStartTime = 0;
let moveDuration = 1000;
let startJointAngles = {};
let endEffectorWorldPos = new THREE.Vector3();
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let originalMaterials = [];
let originalMaterialsSaved = false;
let servoTargetPos = null;
let lastServoTime = 0;
let dragPlane = null;
let dragGrabOffset = new THREE.Vector3();
let dragTargetWorldPos = new THREE.Vector3();
let dragTargetActive = false;
let dragStartAngles = null;
let dragTargetBall = null;
let appConfig = {
  display: {
    cameraPosition: { x: -0.340, y: 0.250, z: -0.500 },
    robotRotationX: -Math.PI / 2,
    robotPositionY: 0.02
  }
};

function t(key) {
  const currentLang = localStorage.getItem('language') || 'zh';
  const i18nObj = window.i18n || {};
  const langObj = i18nObj[currentLang] || {};
  return langObj[key] || key;
}

const jointSliders = {
    joint1: document.getElementById('joint1'),
    joint2: document.getElementById('joint2'),
    joint3: document.getElementById('joint3'),
    joint4: document.getElementById('joint4'),
    joint5: document.getElementById('joint5'),
    gripper: document.getElementById('gripper')
};

loadConfig().then(() => init());

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (response.ok) {
      const config = await response.json();
      if (config.display) {
        appConfig.display = { ...appConfig.display, ...config.display };
        console.log('✓ Config loaded from server:', appConfig);
      }
    }
  } catch (err) {
    console.log('⚠ Using default config (server config not available)');
  }
}

function init() {
    try {
        if (typeof THREE === 'undefined') {
            throw new Error('THREE.js is not loaded. Please check the script tags.');
        }

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);

        camera = new THREE.PerspectiveCamera(
            60,
            (window.innerWidth - 350) / window.innerHeight,
            0.1,
            1000
        );
        camera.position.set(
          appConfig.display.cameraPosition.x,
          appConfig.display.cameraPosition.y,
          appConfig.display.cameraPosition.z
        );

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth - 350, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        controls = createSimpleOrbitControls(camera, renderer.domElement);
        
        setupLights();
        addGroundGrid();
        loadURDF();
        setupEventListeners();
        animate();

    } catch (error) {
        console.error('Initialization error:', error);
        showError('Initialization failed: ' + error.message);
    }
}

function createSimpleOrbitControls(camera, domElement) {
    let isRotating = false;
    let isPanning = false;
    let mouseX = 0, mouseY = 0;
    let panStart = new THREE.Vector2();
    let target = new THREE.Vector3(0, 0.15, 0);
    let spherical = new THREE.Spherical();
    let sphericalDelta = new THREE.Spherical();
    let panOffset = new THREE.Vector3();
    
    const offset = new THREE.Vector3();
    const quat = new THREE.Quaternion().setFromUnitVectors(camera.up, new THREE.Vector3(0, 1, 0));
    const quatInverse = quat.clone().invert();
    
    function update() {
        offset.copy(camera.position).sub(target);
        offset.applyQuaternion(quat);
        spherical.setFromVector3(offset);
        spherical.theta += sphericalDelta.theta;
        spherical.phi += sphericalDelta.phi;
        spherical.phi = Math.max(0.01, Math.min(Math.PI - 0.01, spherical.phi));
        spherical.radius *= sphericalDelta.radius;
        spherical.radius = Math.max(0.1, Math.min(10, spherical.radius));
        offset.setFromSpherical(spherical);
        offset.applyQuaternion(quatInverse);
        camera.position.copy(target).add(offset);
        camera.lookAt(target);
        
        target.add(panOffset);
        
        sphericalDelta.theta *= 0.9;
        sphericalDelta.phi *= 0.9;
        sphericalDelta.radius = 1;
        panOffset.set(0, 0, 0);
    }
    
    function onMouseDown(event) {
        event.preventDefault();
        if (event.button === 0 && orbitApi.enableRotate) {
            isRotating = true;
            mouseX = event.clientX;
            mouseY = event.clientY;
        } else if (event.button === 2 && orbitApi.enablePan) {
            isPanning = true;
            panStart.set(event.clientX, event.clientY);
        }
    }
    
    function onMouseMove(event) {
        if (isRotating) {
            const deltaX = event.clientX - mouseX;
            const deltaY = event.clientY - mouseY;
            sphericalDelta.theta -= deltaX * 0.005;
            sphericalDelta.phi -= deltaY * 0.005;
            mouseX = event.clientX;
            mouseY = event.clientY;
        }
        
        if (isPanning) {
            var deltaX = event.clientX - panStart.x;
            var deltaY = event.clientY - panStart.y;
            
            var distance = camera.position.distanceTo(target);
            var panSpeed = distance * 0.002;
            
            var right = new THREE.Vector3();
            var up = new THREE.Vector3(0, 1, 0);
            camera.getWorldDirection(right);
            right.cross(up).normalize();
            
            panOffset.copy(right).multiplyScalar(-deltaX * panSpeed);
            panOffset.y += deltaY * panSpeed;
            
            panStart.set(event.clientX, event.clientY);
        }
    }
    
    function onMouseUp(event) {
        if (event.button === 0) isRotating = false;
        if (event.button === 2) isPanning = false;
    }
    
    function onMouseWheel(event) {
        event.preventDefault();
        if (event.deltaY > 0) {
            sphericalDelta.radius *= 1.1;
        } else {
            sphericalDelta.radius *= 0.9;
        }
    }
    
    function onContextMenu(event) {
        event.preventDefault();
    }
    
    const orbitApi = {
        update: update,
        target: target,
        enableRotate: true,
        enablePan: true,
        enableDamping: true,
        dampingFactor: 0.05
    };

    domElement.addEventListener('mousedown', onMouseDown);
    domElement.addEventListener('mousemove', onMouseMove);
    domElement.addEventListener('mouseup', onMouseUp);
    domElement.addEventListener('mouseleave', onMouseUp);
    domElement.addEventListener('wheel', onMouseWheel, { passive: false });
    domElement.addEventListener('contextmenu', onContextMenu);
    
    return orbitApi;
}

function setupLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
    directionalLight.position.set(5, 10, 7);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0x00d4ff, 0.4);
    fillLight.position.set(-5, 3, -5);
    scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0x7c3aed, 0.3);
    backLight.position.set(0, 5, -10);
    scene.add(backLight);
}

function addAxisIndicator() {
    var axisGroup = new THREE.Group();
    axisGroup.position.set(-0.46, 0.001, -0.46);

    var arrowLen = 0.06;
    var headLen = 0.012;
    var headRadius = 0.004;

    var axes = [
        { dir: [1, 0, 0], color: 0xff3333, label: 'X' },
        { dir: [0, 1, 0], color: 0x33cc33, label: 'Y' },
        { dir: [0, 0, 1], color: 0x3388ff, label: 'Z' }
    ];

    axes.forEach(function(ax) {
        var vec = new THREE.Vector3(ax.dir[0], ax.dir[1], ax.dir[2]);
        var arrow = new THREE.ArrowHelper(vec, new THREE.Vector3(0, 0, 0), arrowLen, ax.color, headLen, headRadius);
        axisGroup.add(arrow);

        var tipPos = vec.clone().multiplyScalar(arrowLen + 0.015);
        var sprite = makeTextSprite(ax.label, ax.color);
        sprite.position.copy(tipPos);
        axisGroup.add(sprite);
    });

    scene.add(axisGroup);
}

function makeTextSprite(text, color) {
    var canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    var ctx = canvas.getContext('2d');
    ctx.font = 'bold 44px Arial';
    ctx.fillStyle = '#' + color.toString(16).padStart(6, '0');
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 32, 32);

    var tex = new THREE.CanvasTexture(canvas);
    var mat = new THREE.SpriteMaterial({ map: tex, depthTest: false });
    var spr = new THREE.Sprite(mat);
    spr.scale.set(0.025, 0.025, 1);
    return spr;
}

function addGroundGrid() {
    const gridHelper = new THREE.GridHelper(1, 20, 0x444444, 0x333333);
    gridHelper.position.y = -0.001;
    scene.add(gridHelper);

    addAxisIndicator();

    const groundGeometry = new THREE.PlaneGeometry(2, 2);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x222222,
        roughness: 0.8,
        metalness: 0.2
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.002;
    ground.receiveShadow = true;
    scene.add(ground);
}

function loadURDF() {
    try {
        updateStatus('Loading URDF model...');
        updateLoadingText('Parsing URDF file...');

        if (typeof URDFLoader === 'undefined') {
            throw new Error('URDFLoader is not loaded. Please check the script tags.');
        }

        const manager = new THREE.LoadingManager();
        
        manager.onProgress = function(url, itemsLoaded, itemsTotal) {
            const progress = Math.round((itemsLoaded / itemsTotal) * 100);
            updateLoadingText('Loading model... ' + progress + '%');
        };

        manager.onError = function(url) {
            console.error('Error loading:', url);
            showError('Failed to load: ' + url);
        };

        manager.onLoad = function() {
            if (!robot) return;
            
            var meshCount = 0;
            originalMaterials = [];
            robot.traverse(function(child) {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                    child.material = new THREE.MeshStandardMaterial({
                        color: 0xff0000,
                        roughness: 0.4,
                        metalness: 0.2,
                        side: THREE.DoubleSide
                    });
                    var m = child.material;
                    originalMaterials.push({
                        mesh: child,
                        props: {
                            color: m.color.getHex(),
                            transparent: m.transparent,
                            opacity: m.opacity,
                            roughness: m.roughness,
                            metalness: m.metalness,
                            emissive: m.emissive ? m.emissive.getHex() : 0x000000,
                            emissiveIntensity: m.emissiveIntensity || 0
                        }
                    });
                    meshCount++;
                }
            });
            originalMaterialsSaved = true;
            console.log('Recolored ' + meshCount + ' meshes to red, saved ' + originalMaterials.length + ' material snapshots');
        };

        const loader = new URDFLoader(manager);
        loader.packages = window.location.origin + '/api';
        
        loader.load(
            '/api/urdf',
            function(result) {
                robot = result;

                robot.traverse(function(child) {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                robot.rotation.x = appConfig.display.robotRotationX;
                robot.position.y = appConfig.display.robotPositionY;
                scene.add(robot);

                const defaultPose = { joint1: 0, joint2: 5, joint3: 65, joint4: 30, joint5: 0, gripper: 0 };
                Object.keys(defaultPose).forEach(function(name) {
                    currentJointAngles[name] = 0;
                    if (jointSliders[name]) {
                        jointSliders[name].value = 0;
                        updateJointDisplay(name, 0);
                    }
                    setJointAngle(name, 0);
                });

                createGhostRobot();

                startJointAngles = { joint1: 0, joint2: 0, joint3: 0, joint4: 0, joint5: 0, gripper: 0 };
                targetJointAngles = { ...defaultPose };
                isMovingToTarget = true;
                moveStartTime = Date.now();
                moveDuration = 1500;

                hideLoading();
                updateStatus(t('modelLoaded'));

                console.log('Robot loaded successfully');
                console.log('Joints available:', robot.joints ? Object.keys(robot.joints) : 'No joints found');

                if (!robot.joints || Object.keys(robot.joints).length === 0) {
                    console.warn('Warning: No joints found in the model');
                    updateStatus(t('modelNoJoints'));
                }
            },
            
            undefined,
            
            function(error) {
                console.error('Error loading URDF:', error);
                showError('Failed to load URDF model: ' + (error.message || error));
                hideLoading();
            }
        );

    } catch (error) {
        console.error('URDF loading error:', error);
        showError('Failed to initialize URDF loader: ' + error.message);
        hideLoading();
    }
}

function setupEventListeners() {
    Object.keys(jointSliders).forEach(function(jointName) {
        const slider = jointSliders[jointName];
        slider.addEventListener('input', function(e) {
            const degrees = parseFloat(e.target.value);
            const radians = degrees * (Math.PI / 180);
            
            updateJointDisplay(jointName, degrees);
            
            if (robot) {
                setJointAngle(jointName, radians);
            }
            
            currentJointAngles[jointName] = degrees;
        });
    });

    window.addEventListener('resize', onWindowResize);

    renderer.domElement.addEventListener('click', onSceneClick);
    
    setTimeout(() => {
        setupDragInteraction();
    }, 1000);
}

function setJointAngle(jointName, angle) {
    if (!robot) {
        console.warn('Robot not available yet');
        return;
    }

    if (!robot.joints) {
        console.warn('Robot has no joints property');
        return;
    }

    let actualJointName = jointName;
    if (jointName === 'gripper') {
        actualJointName = 'r_joint';
    }

    const joint = robot.joints[actualJointName];
    
    if (joint) {
        if (typeof joint.setAngle === 'function') {
            joint.setAngle(-angle);
        } else if (typeof joint.setJointValue === 'function') {
            joint.setJointValue(-angle);
        } else {
            console.warn('Joint ' + actualJointName + ' has no angle method, trying rotation');
            if (joint.rotateOnAxis) {
                const axis = joint.axis || new THREE.Vector3(0, 0, 1);
                joint.rotateOnAxis(axis, -angle - (joint.angle || 0));
            }
        }
        
        if (jointName === 'gripper') {
            const lJoint = robot.joints['l_joint'];
            if (lJoint) {
                if (typeof lJoint.setAngle === 'function') {
                    lJoint.setAngle(angle);
                } else if (typeof lJoint.setJointValue === 'function') {
                    lJoint.setJointValue(angle);
                }
            }
        }
    } else {
        console.warn('Joint ' + actualJointName + ' not found. Available joints:', Object.keys(robot.joints));
    }
}

function updateJointDisplay(jointName, value) {
    const display = document.getElementById(jointName + '-value');
    if (display) {
        display.textContent = value.toFixed(2) + '°';
    }
}

window.resetJoints = function() {
    const defaultPose = { joint1: 0, joint2: 5, joint3: 65, joint4: 30, joint5: 0, gripper: 0 };
    Object.keys(jointSliders).forEach(function(jointName) {
        const val = defaultPose[jointName] || 0;
        jointSliders[jointName].value = val;
        currentJointAngles[jointName] = val;
        updateJointDisplay(jointName, val);
        setJointAngle(jointName, val * Math.PI / 180);
    });
};

const DEFAULT_POSE = { joint1: 0, joint2: 5, joint3: 65, joint4: 30, joint5: 0, gripper: 0 };

window.generateTrajectory = function() {
    if (!robot) return;

    isAnimating = false;
    isMovingToTarget = false;
    isDraggingEndEffector = false;
    servoTargetPos = null;

    restoreOriginalMaterial();

    const sliderAngles = {};
    Object.keys(DEFAULT_POSE).forEach(function(name) {
        sliderAngles[name] = parseFloat(jointSliders[name].value);
    });

    Object.keys(DEFAULT_POSE).forEach(function(name) {
        currentJointAngles[name] = DEFAULT_POSE[name];
        if (jointSliders[name]) {
            jointSliders[name].value = DEFAULT_POSE[name];
            updateJointDisplay(name, DEFAULT_POSE[name]);
        }
        setJointAngle(name, DEFAULT_POSE[name] * Math.PI / 180);
    });

    applyGhostMaterial();

    startJointAngles = { ...DEFAULT_POSE };
    targetJointAngles = { ...sliderAngles };
    isMovingToTarget = true;
    moveStartTime = Date.now();
    moveDuration = 1200;

    console.log('🛤️ Trajectory: default(RED) → ghost(PURPLE) → slider');
};

window.toggleAnimation = function() {
    isAnimating = !isAnimating;
    var btn = event.target;
    
    if (isAnimating) {
        btn.textContent = t('stopAnimationBtn');
        btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        animationTime = 0;
    } else {
        btn.textContent = t('animationBtn');
        btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        resetJoints();
    }
};

function runAnimation() {
    if (!isAnimating || !robot) return;

    animationTime += 0.02;

    var angles = {
        joint1: Math.sin(animationTime * 0.7) * 1.5,
        joint2: Math.sin(animationTime * 0.9) * 0.8 + 0.5,
        joint3: Math.sin(animationTime * 1.1) * 1.2,
        joint4: Math.sin(animationTime * 1.3) * 0.8,
        joint5: Math.sin(animationTime * 1.5) * 1.0,
        gripper: Math.abs(Math.sin(animationTime * 2.0)) * 0.8
    };

    Object.keys(angles).forEach(function(jointName) {
        var degrees = angles[jointName] * (180 / Math.PI);
        jointSliders[jointName].value = degrees;
        updateJointDisplay(jointName, degrees);
        setJointAngle(jointName, angles[jointName]);
    });
}

function onSceneClick(event) {
    if (!isGrabMode || isGrabbing) return;

    var rect = renderer.domElement.getBoundingClientRect();
    var clickX = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    var clickY = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    var clickRaycaster = new THREE.Raycaster();
    clickRaycaster.setFromCamera(new THREE.Vector2(clickX, clickY), camera);

    var intersects = clickRaycaster.intersectObjects(grabItems, false);
    if (intersects.length > 0) {
        var clickedMesh = intersects[0].object;
        var idx = grabItems.indexOf(clickedMesh);
        if (idx >= 0) {
            selectGrabItem(idx);
        }
    }
}

let isGrabMode = false;
let grabItems = [];
let storageBox = null;
let selectedItem = null;
let isGrabbing = false;
let grabSequence = [];
let grabStepIndex = 0;
let grabStepStartTime = 0;
let grabbedObject = null;
let grabAttachOffset = new THREE.Vector3(0, 0, 0);
let grabDesiredAttachOffset = new THREE.Vector3(0, -0.025, 0);
let grabMoveStartAngles = null;
let grabPlacedCount = 0;
const GRAB_ITEM_CONFIGS = [
    { nameKey: 'grabItemRedCube', name: '红色方块', nameEn: 'Red Cube', color: 0xe74c3c, geo: 'box', size: [0.028, 0.028, 0.028], pos: [-0.08, 0.014, -0.20] },
    { nameKey: 'grabItemBlueSphere', name: '蓝色球体', nameEn: 'Blue Sphere', color: 0x3498db, geo: 'sphere', size: [0.018, 16, 16], pos: [-0.02, 0.014, -0.25] },
    { nameKey: 'grabItemGreenCylinder', name: '绿色圆柱', nameEn: 'Green Cylinder', color: 0x27ae60, geo: 'cylinder', size: [0.013, 0.035, 16], pos: [0.04, 0.014, -0.23] },
    { nameKey: 'grabItemOrangeCone', name: '橙色圆锥', nameEn: 'Orange Cone', color: 0xe67e22, geo: 'cone', size: [0.016, 0.035, 16], pos: [0.10, 0.014, -0.19] },
    { nameKey: 'grabItemYellowRing', name: '黄色圆环', nameEn: 'Yellow Ring', color: 0xf1c40f, geo: 'torus', size: [0.014, 0.005, 8, 32], pos: [0.01, 0.017, -0.15] }
];

window.toggleGrabMode = function() {
    isGrabMode = !isGrabMode;
    var btn = document.getElementById('grabTaskBtn');
    var panel = document.getElementById('grab-panel');
    var indicator = document.getElementById('mode-indicator');

    if (isGrabMode) {
        isAnimating = false;
        isDragMode = false;
        isDraggingEndEffector = false;
        servoTargetPos = null;

        var dragBtn = document.getElementById('dragModeBtn');
        if (dragBtn) {
            dragBtn.classList.remove('active');
            dragBtn.textContent = t('dragModeBtn');
        }
        var marker = document.getElementById('end-effector-marker');
        if (marker) marker.style.display = 'none';

        restoreOriginalMaterial();

        createGrabScene();

        btn.classList.add('active');
        btn.textContent = t('exitGrabModeBtn') || '⏹️ Exit Grab';
        btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        panel.style.display = 'block';
        indicator.textContent = t('grabModeActive') || '🤏 Grab Mode - Click items to select';
        indicator.style.display = 'block';
        indicator.style.background = 'rgba(245, 158, 11, 0.9)';

        controls.enableRotate = true;
        controls.enablePan = true;

        console.log('✓ Grab mode enabled - ' + grabItems.length + ' items available');
    } else {
        removeGrabScene();

        btn.classList.remove('active');
        btn.textContent = t('grabTaskBtn') || '🤏 Grab Task';
        btn.style.background = 'linear-gradient(135deg, #f59e0b, #d97706)';
        panel.style.display = 'none';
        indicator.style.display = 'none';

        selectedItem = null;
        isGrabbing = false;
        grabSequence = [];

        console.log('✓ Grab mode disabled');
    }
};

function createGrabScene() {
    removeGrabScene();
    grabItems = [];
    grabPlacedCount = 0;

    GRAB_ITEM_CONFIGS.forEach(function(cfg) {
        var mesh;
        switch (cfg.geo) {
            case 'box':
                mesh = new THREE.Mesh(
                    new THREE.BoxGeometry(cfg.size[0], cfg.size[1], cfg.size[2]),
                    new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.3, metalness: 0.4 })
                );
                break;
            case 'sphere':
                mesh = new THREE.Mesh(
                    new THREE.SphereGeometry(cfg.size[0], cfg.size[1], cfg.size[2]),
                    new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.3, metalness: 0.4 })
                );
                break;
            case 'cylinder':
                mesh = new THREE.Mesh(
                    new THREE.CylinderGeometry(cfg.size[0], cfg.size[0], cfg.size[1], cfg.size[2]),
                    new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.3, metalness: 0.4 })
                );
                break;
            case 'cone':
                mesh = new THREE.Mesh(
                    new THREE.ConeGeometry(cfg.size[0], cfg.size[1], cfg.size[2]),
                    new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.3, metalness: 0.4 })
                );
                break;
            case 'torus':
                mesh = new THREE.Mesh(
                    new THREE.TorusGeometry(cfg.size[0], cfg.size[1], cfg.size[2], cfg.size[3]),
                    new THREE.MeshStandardMaterial({ color: cfg.color, roughness: 0.3, metalness: 0.4 })
                );
                break;
        }

        mesh.position.set(cfg.pos[0], cfg.pos[1], cfg.pos[2]);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData.isGrabItem = true;
        mesh.userData.itemNameKey = cfg.nameKey;
        mesh.userData.itemName = t(cfg.nameKey) || cfg.name;
        mesh.userData.originalColor = cfg.color;
        mesh.userData.originalPosition = cfg.pos.slice();
        mesh.userData.geo = cfg.geo;
        mesh.userData.size = cfg.size.slice();
        mesh.userData.isGrabbed = false;
        mesh.userData.isHeld = false;
        scene.add(mesh);
        grabItems.push(mesh);
    });

    storageBox = createStorageBox();
    scene.add(storageBox);

    populateGrabItemsList();
}

function createStorageBox() {
    var group = new THREE.Group();
    group.userData.isStorageBox = true;
    group.position.set(0.20, 0.01, -0.10);

    var wallThickness = 0.004;
    var wallHeight = 0.05;
    var boxWidth = 0.08;
    var boxDepth = 0.07;
    var glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x88ccff,
        transparent: true,
        opacity: 0.25,
        roughness: 0.1,
        metalness: 0.1,
        transmission: 0.7,
        thickness: 0.002,
        side: THREE.DoubleSide
    });
    var frameMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.3, metalness: 0.7 });
    var bottomMat = new THREE.MeshStandardMaterial({ color: 0xdddddd, roughness: 0.8, metalness: 0.1 });

    var bottom = new THREE.Mesh(new THREE.BoxGeometry(boxWidth, wallThickness, boxDepth), bottomMat);
    bottom.position.y = -wallHeight / 2 + wallThickness / 2;
    bottom.receiveShadow = true;
    group.add(bottom);

    var frontWall = new THREE.Mesh(new THREE.BoxGeometry(boxWidth, wallHeight, wallThickness), glassMat);
    frontWall.position.set(0, 0, boxDepth / 2);
    frontWall.castShadow = true;
    group.add(frontWall);

    var backWall = new THREE.Mesh(new THREE.BoxGeometry(boxWidth, wallHeight, wallThickness), glassMat);
    backWall.position.set(0, 0, -boxDepth / 2);
    backWall.castShadow = true;
    group.add(backWall);

    var leftWall = new THREE.Mesh(new THREE.BoxGeometry(wallThickness, wallHeight, boxDepth), glassMat);
    leftWall.position.set(-boxWidth / 2, 0, 0);
    leftWall.castShadow = true;
    group.add(leftWall);

    var rightWall = new THREE.Mesh(new THREE.BoxGeometry(wallThickness, wallHeight, boxDepth), glassMat);
    rightWall.position.set(boxWidth / 2, 0, 0);
    rightWall.castShadow = true;
    group.add(rightWall);

    var frameGeo = new THREE.BoxGeometry(0.003, wallHeight, 0.003);
    [[-boxWidth/2, boxDepth/2], [boxWidth/2, boxDepth/2], [-boxWidth/2, -boxDepth/2], [boxWidth/2, -boxDepth/2]].forEach(function(corner) {
        var post = new THREE.Mesh(frameGeo, frameMat);
        post.position.set(corner[0], 0, corner[1]);
        post.castShadow = true;
        group.add(post);
    });

    return group;
}

function removeGrabScene() {
    isGrabbing = false;
    grabSequence = [];
    grabStepIndex = 0;
    grabMoveStartAngles = null;
    grabbedObject = null;

    var toRemove = [];
    scene.traverse(function(child) {
        if (child.userData && (child.userData.isGrabItem || child.userData.isStorageBox)) {
            toRemove.push(child);
        }
    });

    toRemove.forEach(function(item) {
        if (item.parent) {
            item.parent.remove(item);
        }
        disposeSceneObject(item);
    });

    grabItems = [];

    storageBox = null;
    selectedItem = null;
    grabPlacedCount = 0;

    var listEl = document.getElementById('grab-items-list');
    if (listEl) listEl.innerHTML = '';
}

function disposeSceneObject(obj) {
    obj.traverse(function(child) {
        if (child.geometry) {
            child.geometry.dispose();
        }
        if (child.material) {
            if (Array.isArray(child.material)) {
                child.material.forEach(function(mat) { mat.dispose(); });
            } else {
                child.material.dispose();
            }
        }
    });
}

function populateGrabItemsList() {
    var listEl = document.getElementById('grab-items-list');
    if (!listEl) return;
    listEl.innerHTML = '';

    grabItems.forEach(function(item, idx) {
        var chip = document.createElement('div');
        chip.className = 'grab-item-chip';
        if (item.userData.isGrabbed) {
            chip.classList.add('grabbed');
        }
        chip.dataset.index = idx;
        chip.onclick = function() { selectGrabItem(idx); };

        var dot = document.createElement('span');
        dot.className = 'item-dot';
        dot.style.backgroundColor = '#' + item.userData.originalColor.toString(16).padStart(6, '0');

        var label = document.createElement('span');
        var displayName = item.userData.itemNameKey ? (t(item.userData.itemNameKey) || item.userData.itemName) : item.userData.itemName;
        label.textContent = displayName;

        chip.appendChild(dot);
        chip.appendChild(label);
        listEl.appendChild(chip);
    });
}

function selectGrabItem(index) {
    if (!isGrabMode || index < 0 || index >= grabItems.length) return;
    if (grabItems[index].userData.isGrabbed) return;

    grabItems.forEach(function(item, i) {
        if (item.material && item.userData.originalColor !== undefined) {
            item.material.emissive.setHex(i === index ? 0xf59e0b : 0x000000);
            item.material.emissiveIntensity = i === index ? 0.4 : 0;
            item.needsUpdate = true;
        }
    });

    selectedItem = grabItems[index];

    var chips = document.querySelectorAll('.grab-item-chip');
    chips.forEach(function(chip, i) {
        chip.classList.toggle('selected', i === index);
    });

    console.log('📦 Selected item:', selectedItem.userData.itemName);
}

window.startGrabSequence = function() {
    if (!isGrabMode || !selectedItem || isGrabbing) {
        if (!selectedItem) {
            alert(isGrabMode ? (localStorage.getItem('language') === 'en' ? 'Please select an item first!' : '请先选择要抓取的物品！') : '');
        }
        return;
    }
    if (selectedItem.userData.isGrabbed) return;

    isGrabbing = true;
    isMovingToTarget = false;
    isDraggingEndEffector = false;
    servoTargetPos = null;
    restoreOriginalMaterial();

    var itemWorldPos = selectedItem.getWorldPosition(new THREE.Vector3());
    var boxWorldPos = storageBox ? storageBox.getWorldPosition(new THREE.Vector3()) : new THREE.Vector3(0.16, 0.01, -0.15);

    var approachHeight = 0.055;
    var pickHeight = 0.020;

    var rawSteps = [
        { type: 'move', target: { x: itemWorldPos.x, y: approachHeight, z: itemWorldPos.z }, duration: 2000 },
        { type: 'move', target: { x: itemWorldPos.x, y: pickHeight, z: itemWorldPos.z }, duration: 1200 },
        { type: 'gripper', value: 75, duration: 500 },
        { type: 'attach' },
        { type: 'move', target: { x: itemWorldPos.x, y: approachHeight, z: itemWorldPos.z }, duration: 1200 },
        { type: 'move', target: { x: boxWorldPos.x - 0.02, y: approachHeight, z: boxWorldPos.z }, duration: 2200 },
        { type: 'move', target: { x: boxWorldPos.x - 0.02, y: pickHeight + 0.006, z: boxWorldPos.z }, duration: 1000 },
        { type: 'gripper', value: 0, duration: 500 },
        { type: 'detach' },
        { type: 'move', target: { x: boxWorldPos.x - 0.02, y: approachHeight, z: boxWorldPos.z }, duration: 800 }
    ];

    grabSequence = [];
    rawSteps.forEach(function(s) {
        grabSequence.push(Object.assign({}, s));
    });

    grabStepIndex = 0;
    grabbedObject = null;
    grabAttachOffset = new THREE.Vector3(0, 0, 0);
    grabDesiredAttachOffset = new THREE.Vector3(0, -0.025, 0);
    grabMoveStartAngles = null;

    console.log('🚀 开始抓取，共 ' + grabSequence.length + ' 步，正在预解算 IK...');
    preSolveCurrentStep();

    var startBtn = document.getElementById('startGrabBtn');
    if (startBtn) startBtn.disabled = true;
};

function preSolveCurrentStep() {
    if (grabStepIndex >= grabSequence.length) return;

    var step = grabSequence[grabStepIndex];

    if (step.type === 'move') {
        step.targetAngles = solveIKForTarget(step.target, 300, 600);

        if (!grabMoveStartAngles) {
            grabMoveStartAngles = {};
            ['joint1','joint2','joint3','joint4','joint5'].forEach(function(j) {
                grabMoveStartAngles[j] = currentJointAngles[j];
            });
        }

        console.log('  步骤 ' + (grabStepIndex+1) + ' IK 解算完成，目标:', JSON.stringify(step.targetAngles));
    }
}

function solveIKForTarget(worldTarget, maxIter, timeoutMs) {
    var savedAngles = {};
    Object.keys(currentJointAngles).forEach(function(k) {
        savedAngles[k] = currentJointAngles[k];
    });

    var startTime = Date.now();
    for (var i = 0; i < maxIter; i++) {
        ServoController.servoStep(
            new THREE.Vector3(worldTarget.x, worldTarget.y, worldTarget.z),
            0.032
        );

        if ((i + 1) % 10 === 0) {
            var eePos = getEndEffectorPosition();
            var dx = worldTarget.x - eePos.x;
            var dy = worldTarget.y - eePos.y;
            var dz = worldTarget.z - eePos.z;
            var dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (dist < 0.006) break;
        }

        if (Date.now() - startTime > timeoutMs) break;
    }

    var result = {};
    ['joint1','joint2','joint3','joint4','joint5'].forEach(function(j) {
        result[j] = currentJointAngles[j];
    });

    Object.keys(savedAngles).forEach(function(j) {
        currentJointAngles[j] = savedAngles[j];
        setJointAngle(j, savedAngles[j] * Math.PI / 180);
        if (jointSliders[j]) {
            jointSliders[j].value = savedAngles[j];
            updateJointDisplay(j, savedAngles[j]);
        }
    });

    return result;
}

function updateGrabAnimation() {
    if (!isGrabbing || grabStepIndex >= grabSequence.length) return;

    var step = grabSequence[grabStepIndex];

    if (grabbedObject && grabbedObject.visible && grabbedObject.parent && grabbedObject.userData.isHeld) {
        var eePos = getEndEffectorPosition();
        grabAttachOffset.lerp(grabDesiredAttachOffset, 0.06);
        var targetPos = eePos.clone().add(grabAttachOffset);
        var minY = getGrabItemHalfHeight(grabbedObject);
        targetPos.y = Math.max(targetPos.y, minY);
        grabbedObject.position.lerp(targetPos, 0.35);
    }

    switch (step.type) {
        case 'move':
            executeMoveStep(step);
            break;
        case 'gripper':
            executeGripperStep(step);
            break;
        case 'attach':
            attachGrabbedObject();
            advanceGrabStep();
            break;
        case 'detach':
            detachGrabbedObject();
            advanceGrabStep();
            break;
    }
}

function executeMoveStep(step) {
    if (!step.targetAngles) {
        console.warn('⚠️ 步骤缺少 IK 解算结果，跳过');
        advanceGrabStep();
        return;
    }

    if (!step._startTime) {
        step._startTime = Date.now();
        step._startAngles = {};
        ['joint1','joint2','joint3','joint4','joint5'].forEach(function(j) {
            step._startAngles[j] = currentJointAngles[j];
        });
    }

    var elapsed = Date.now() - step._startTime;
    var progress = Math.min(elapsed / step.duration, 1);
    var eased = easeInOutCubic(progress);

    ['joint1','joint2','joint3','joint4','joint5'].forEach(function(j) {
        var from = step._startAngles[j] || 0;
        var to = step.targetAngles[j] || 0;
        var angle = from + (to - from) * eased;

        currentJointAngles[j] = angle;
        setJointAngle(j, angle * Math.PI / 180);

        if (jointSliders[j]) {
            jointSliders[j].value = angle;
            updateJointDisplay(j, angle);
        }
    });

    if (progress >= 1) {
        delete step._startTime;
        delete step._startAngles;
        advanceGrabStep();
    }
}

function executeGripperStep(step) {
    var elapsed = Date.now() - grabStepStartTime;
    var progress = Math.min(elapsed / step.duration, 1);
    var eased = easeInOutCubic(progress);
    var gripperValue = step.value * eased;
    setJointAngle('gripper', gripperValue * Math.PI / 180);
    if (jointSliders.gripper) {
        jointSliders.gripper.value = gripperValue;
        updateJointDisplay('gripper', gripperValue);
    }
    currentJointAngles.gripper = gripperValue;

    if (progress >= 1) {
        advanceGrabStep();
    }
}

function getGrabItemHalfHeight(item) {
    if (!item || !item.geometry) return 0.012;
    if (!item.geometry.boundingBox) {
        item.geometry.computeBoundingBox();
    }
    var box = item.geometry.boundingBox;
    return Math.max(0.006, ((box.max.y - box.min.y) * item.scale.y) / 2);
}

function getGrabItemContactRadius(item) {
    if (!item || !item.geometry) return 0.035;
    if (!item.geometry.boundingSphere) {
        item.geometry.computeBoundingSphere();
    }
    return Math.max(0.02, item.geometry.boundingSphere.radius * Math.max(item.scale.x, item.scale.y, item.scale.z));
}

function attachGrabbedObject() {
    if (selectedItem && !selectedItem.userData.isGrabbed) {
        var eePos = getEndEffectorPosition();
        var itemPos = selectedItem.getWorldPosition(new THREE.Vector3());
        var contactRadius = getGrabItemContactRadius(selectedItem) + 0.045;

        grabbedObject = selectedItem;
        grabAttachOffset.copy(itemPos).sub(eePos);
        if (grabAttachOffset.length() > contactRadius) {
            grabAttachOffset.setLength(contactRadius);
        }
        grabDesiredAttachOffset.set(0, -Math.max(0.018, getGrabItemHalfHeight(selectedItem) + 0.010), 0);

        grabbedObject.position.copy(itemPos);
        grabbedObject.visible = true;
        grabbedObject.userData.isHeld = true;

        console.log('🔗 抓取:', grabbedObject.userData.itemName);
    }
}

function detachGrabbedObject() {
    if (grabbedObject && storageBox) {
        var boxPos = storageBox.getWorldPosition(new THREE.Vector3());
        var slots = [
            [-0.018, -0.015],
            [0.018, -0.012],
            [-0.018, 0.016],
            [0.018, 0.016],
            [0, 0]
        ];
        var slot = slots[grabPlacedCount % slots.length];
        grabbedObject.position.set(
            boxPos.x + slot[0],
            getGrabItemHalfHeight(grabbedObject) + 0.004,
            boxPos.z + slot[1]
        );
        grabbedObject.rotation.set(0, grabPlacedCount * 0.45, 0);
        grabbedObject.userData.isHeld = false;
        grabbedObject.userData.isGrabbed = true;
        grabPlacedCount++;

        var chipIdx = grabItems.indexOf(selectedItem);
        if (chipIdx >= 0) {
            var chips = document.querySelectorAll('.grab-item-chip');
            if (chips[chipIdx]) chips[chipIdx].classList.add('grabbed');
        }

        console.log('📥 放入盒中:', grabbedObject.userData.itemName);
        grabbedObject = null;
        selectedItem = null;

        var chips = document.querySelectorAll('.grab-item-chip');
        chips.forEach(function(c) { c.classList.remove('selected'); });
    }
}

function advanceGrabStep() {
    grabStepIndex++;

    if (grabStepIndex >= grabSequence.length) {
        finishGrabSequence();
    } else {
        var nextStep = grabSequence[grabStepIndex];
        if (nextStep.type === 'move') {
            nextStep.targetAngles = solveIKForTarget(nextStep.target, 300, 600);
        }
        console.log('➡️ 步骤 ' + (grabStepIndex + 1) + '/' + grabSequence.length + ': ' + nextStep.type);
    }
}

function finishGrabSequence() {
    isGrabbing = false;
    grabSequence = [];
    grabStepIndex = 0;

    if (grabbedObject && grabbedObject.parent) {
        scene.remove(grabbedObject);
    }
    grabbedObject = null;

    var startBtn = document.getElementById('startGrabBtn');
    if (startBtn) startBtn.disabled = false;

    var indicator = document.getElementById('mode-indicator');
    if (indicator) indicator.textContent = t('grabComplete') || '✅ 抓取完成！选择下一个物品';

    console.log('✅ 抓取完成！');
}

function onWindowResize() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar && sidebar.classList.contains('collapsed');
    const sidebarWidth = isCollapsed ? 0 : 350;
    
    camera.aspect = (window.innerWidth - sidebarWidth) / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth - sidebarWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    
    if (controls && controls.update) {
        controls.update();
    }
    
    runAnimation();
    
    updateSmoothMove();
    
    if (isDragMode) {
        updateEndEffectorMarker();
    }
    
    if (isDraggingEndEffector && servoTargetPos) {
        const now = performance.now();
        const dt = lastServoTime > 0 ? (now - lastServoTime) / 1000 : 0.016;
        lastServoTime = now;
        const clampedDt = Math.min(dt, 0.05);
        const substeps = Math.max(1, Math.ceil(clampedDt / 0.016));
        let servoResult = null;
        for (let i = 0; i < substeps; i++) {
            servoResult = ServoController.servoStep(servoTargetPos, clampedDt / substeps);
        }

        const ghostIndicator = document.getElementById('ghost-indicator');
        if (ghostIndicator && servoResult) {
            ghostIndicator.textContent = `${t('ghostInfo')} err=${(servoResult.error * 1000).toFixed(1)}mm`;
        }
    } else {
        lastServoTime = 0;
    }

    updateGrabAnimation();

    var camInfo = document.getElementById('cam-pos');
    if (camInfo && camera) {
        camInfo.textContent = 'X=' + camera.position.x.toFixed(3) + ' Y=' + camera.position.y.toFixed(3) + ' Z=' + camera.position.z.toFixed(3);
    }
    
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }
}

function updateStatus(text) {
    var statusEl = document.getElementById('status-text');
    if (statusEl) {
        statusEl.textContent = text;
    }
}

function updateLoadingText(text) {
    var loadingEl = document.getElementById('loading-text');
    if (loadingEl) {
        loadingEl.textContent = text;
    }
}

function hideLoading() {
    setTimeout(function() {
        var loading = document.getElementById('loading');
        if (loading) {
            loading.style.opacity = '0';
            loading.style.transition = 'opacity 0.5s ease';
            setTimeout(function() {
                loading.style.display = 'none';
            }, 500);
        }
    }, 500);
}

function showError(message) {
    console.error(message);
    var errorDiv = document.getElementById('error');
    var errorText = document.getElementById('error-text');

    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.style.display = 'block';
    }

    hideLoading();
}

function createGhostRobot() {
    if (!robot) {
        console.warn('Cannot create ghost: robot not loaded');
        return;
    }
    console.log('✓ Ghost system ready (materials already saved at load time, count=' + originalMaterials.length + ')');
}

function applyGhostMaterial() {
    if (!robot) return;

    robot.traverse(function(child) {
        if (child.isMesh && child.material) {
            var m = child.material;
            m.color.setHex(0x7c3aed);
            m.transparent = true;
            m.opacity = 0.5;
            m.roughness = 0.3;
            m.metalness = 0.6;
            m.emissive.setHex(0x7c3aed);
            m.emissiveIntensity = 0.2;
            m.castShadow = false;
            m.needsUpdate = true;
        }
    });

    console.log('✓ Applied ghost material (purple)');
}

function restoreOriginalMaterial() {
    if (!robot || originalMaterials.length === 0) {
        console.warn('⚠️ No saved materials to restore, count=' + originalMaterials.length);
        return;
    }

    var restoredCount = 0;
    originalMaterials.forEach(function(item) {
        if (item.mesh && item.mesh.material && item.props) {
            var m = item.mesh.material;
            var p = item.props;
            m.color.setHex(p.color);
            m.transparent = p.transparent;
            m.opacity = p.opacity;
            m.roughness = p.roughness;
            m.metalness = p.metalness;
            m.emissive.setHex(p.emissive);
            m.emissiveIntensity = p.emissiveIntensity;
            m.castShadow = true;
            m.needsUpdate = true;
            restoredCount++;
        }
    });

    console.log('✓ Restored original material, ' + restoredCount + '/' + originalMaterials.length + ' meshes, color=0x' + (originalMaterials[0] ? originalMaterials[0].props.color.toString(16) : 'N/A'));
}

window.toggleSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    if (sidebar.classList.contains('collapsed')) {
        sidebar.classList.remove('collapsed');
        toggleBtn.textContent = '◀';
        toggleBtn.style.right = '350px';
        onWindowResize();
    } else {
        sidebar.classList.add('collapsed');
        toggleBtn.textContent = '▶';
        toggleBtn.style.right = '0px';
        setTimeout(() => {
            onWindowResize();
        }, 300);
    }
};

window.toggleDragMode = function() {
    isDragMode = !isDragMode;
    const btn = document.getElementById('dragModeBtn');
    const marker = document.getElementById('end-effector-marker');
    const indicator = document.getElementById('mode-indicator');
    const ghostIndicator = document.getElementById('ghost-indicator');

    if (isDragMode) {
        btn.classList.add('active');
        btn.textContent = t('exitDragModeBtn');
        marker.style.display = 'block';
        indicator.style.display = 'block';
        indicator.textContent = t('dragModeActive');
        ghostIndicator.style.display = 'block';
        ghostIndicator.textContent = t('ghostInfo');

        dragTargetWorldPos.copy(getEndEffectorPosition());
        dragTargetActive = true;
        updateDragTargetBall(dragTargetWorldPos);
        updateEndEffectorMarker();
        controls.enableRotate = true;
        controls.enablePan = true;

        console.log('✓ Drag mode enabled - real-time IK following (MoveIt2 style)');
    } else {
        btn.classList.remove('active');
        btn.textContent = t('dragModeBtn');
        marker.style.display = 'none';
        indicator.style.display = 'none';
        ghostIndicator.style.display = 'none';
        isDraggingEndEffector = false;
        servoTargetPos = null;
        dragPlane = null;
        dragTargetActive = false;
        dragStartAngles = null;
        if (dragTargetBall) {
            dragTargetBall.visible = false;
        }
        isMovingToTarget = false;

        restoreOriginalMaterial();

        controls.enableRotate = true;
        controls.enablePan = true;

        console.log('✓ Drag mode disabled - Normal mode restored');
    }
};

function getEndEffectorPosition() {
    if (!robot || !robot.joints) return new THREE.Vector3(0, 0, 0);

    robot.updateMatrixWorld(true);

    const preferredNames = ['grasping_frame', 'gripper_base', 'link5'];
    for (let i = 0; i < preferredNames.length; i++) {
        const obj = robot.getObjectByName ? robot.getObjectByName(preferredNames[i]) : null;
        if (obj) {
            const pos = new THREE.Vector3();
            obj.getWorldPosition(pos);
            return pos;
        }
    }
    
    let endEffector = null;
    robot.traverse(function(child) {
        if (child.isMesh && child.name && (
            child.name.toLowerCase().includes('gripper') ||
            child.name.toLowerCase().includes('finger') ||
            child.name.toLowerCase().includes('end')
        )) {
            if (!endEffector) {
                endEffector = child;
            }
        }
    });
    
    if (!endEffector) {
        const joints = Object.keys(robot.joints);
        if (joints.length > 0) {
            const lastJoint = robot.joints[joints[joints.length - 1]];
            if (lastJoint) {
                return new THREE.Vector3().setFromMatrixPosition(lastJoint.matrixWorld);
            }
        }
        return new THREE.Vector3(0, 0.2, 0);
    }
    
    const pos = new THREE.Vector3();
    endEffector.getWorldPosition(pos);
    return pos;
}

function updateEndEffectorMarker() {
    if (!isDragMode || !renderer || !camera) return;
    
    const worldPos = dragTargetActive ? dragTargetWorldPos : getEndEffectorPosition();
    if (!dragTargetActive) {
        dragTargetWorldPos.copy(worldPos);
    }
    endEffectorWorldPos.copy(getEndEffectorPosition());
    
    const screenPos = worldPos.clone().project(camera);
    
    const x = (screenPos.x * 0.5 + 0.5) * renderer.domElement.clientWidth;
    const y = (-screenPos.y * 0.5 + 0.5) * renderer.domElement.clientHeight;
    
    const marker = document.getElementById('end-effector-marker');
    if (marker) {
        marker.style.left = (x - 10) + 'px';
        marker.style.top = (y - 10) + 'px';
    }

    updateDragTargetBall(worldPos);
}

function ensureDragTargetBall() {
    if (dragTargetBall || !scene) return dragTargetBall;

    const geometry = new THREE.SphereGeometry(0.012, 24, 16);
    const material = new THREE.MeshStandardMaterial({
        color: 0x00d4ff,
        emissive: 0x00d4ff,
        emissiveIntensity: 0.45,
        roughness: 0.25,
        metalness: 0.1
    });
    dragTargetBall = new THREE.Mesh(geometry, material);
    dragTargetBall.visible = false;
    dragTargetBall.renderOrder = 10;
    scene.add(dragTargetBall);
    return dragTargetBall;
}

function updateDragTargetBall(worldPos) {
    const ball = ensureDragTargetBall();
    if (!ball || !worldPos) return;
    ball.position.copy(worldPos);
    ball.visible = isDragMode;
}

const ArmIK = {
    linkLengths: {
        l1: 0.056,
        l2: 0.103,
        l3: 0.097,
        l4: 0.065,
        l5: 0.038
    },
    
    solve: function(x, y, z, alpha) {
        const { l1, l2, l3, l4, l5 } = this.linkLengths;
        
        alpha = alpha * Math.PI / 180;
        
        let theta1 = Math.atan2(y, x);
        
        const r = Math.sqrt(x * x + y * y);
        const zf = z - l1 - l5 * Math.sin(alpha);
        const rf = r - l5 * Math.cos(alpha);
        
        const cosTheta3 = (zf * zf + rf * rf - l2 * l2 - l3 * l3) / (2 * l2 * l3);
        
        if (Math.abs(cosTheta3) > 1) {
            console.warn('IK: No solution - out of reach');
            return null;
        }
        
        let theta3 = Math.acos(cosTheta3);
        
        const k1 = l2 + l3 * Math.cos(theta3);
        const k2 = l3 * Math.sin(theta3);
        
        let theta2 = Math.atan2(zf, rf) - Math.atan2(k2, k1);
        
        let theta4 = alpha - theta2 - theta3;
        
        theta1 = theta1 * 180 / Math.PI;
        theta2 = theta2 * 180 / Math.PI;
        theta3 = theta3 * 180 / Math.PI;
        theta4 = theta4 * 180 / Math.PI;
        
        theta1 = Math.max(-120, Math.min(120, theta1));
        theta2 = Math.max(-90, Math.min(90, theta2));
        theta3 = Math.max(-120, Math.min(120, theta3));
        theta4 = Math.max(-120, Math.min(120, theta4));
        
        return {
            joint1: theta1,
            joint2: theta2,
            joint3: theta3,
            joint4: theta4,
            joint5: 0
        };
    },
    
    setPitchRanges: function(coordinate_data, alpha_target, alpha_min, alpha_max, d) {
        d = d || 0.01;
        const [x, y, z] = coordinate_data;
        
        let bestResult = null;
        let bestAlpha = alpha_target;
        let minDiff = Infinity;
        
        for (let alpha = alpha_min; alpha <= alpha_max; alpha += d) {
            const result = this.solve(x, y, z, alpha);
            if (result) {
                const diff = Math.abs(alpha - alpha_target);
                if (diff < minDiff) {
                    minDiff = diff;
                    bestResult = result;
                    bestAlpha = alpha;
                }
            }
        }
        
        return bestResult ? { angles: bestResult, alpha: bestAlpha } : null;
    }
};

const ServoController = {
    kp: 14.0,
    damping: 0.025,
    maxJointSpeed: 260,
    jointNames: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5'],

    jointLimits: {
        joint1: [-120, 120],
        joint2: [-90, 90],
        joint3: [-120, 120],
        joint4: [-120, 120],
        joint5: [-120, 120]
    },

    applyModelAngles: function(angles) {
        this.jointNames.forEach(function(name) {
            setJointAngle(name, (angles[name] || 0) * Math.PI / 180);
        });
        if (robot) {
            robot.updateMatrixWorld(true);
        }
    },

    computeJacobian: function(angles) {
        const epsDeg = 0.45;
        const epsRad = epsDeg * Math.PI / 180;
        const baseAngles = {};
        this.jointNames.forEach(function(name) {
            baseAngles[name] = angles[name] || 0;
        });

        const J = [[], [], []];

        for (let i = 0; i < this.jointNames.length; i++) {
            const name = this.jointNames[i];
            const plusAngles = { ...baseAngles };
            const minusAngles = { ...baseAngles };
            plusAngles[name] += epsDeg;
            minusAngles[name] -= epsDeg;

            this.applyModelAngles(plusAngles);
            const plusPos = getEndEffectorPosition();

            this.applyModelAngles(minusAngles);
            const minusPos = getEndEffectorPosition();

            J[0][i] = (plusPos.x - minusPos.x) / (2 * epsRad);
            J[1][i] = (plusPos.y - minusPos.y) / (2 * epsRad);
            J[2][i] = (plusPos.z - minusPos.z) / (2 * epsRad);
        }

        this.applyModelAngles(baseAngles);
        return J;
    },

    invert3x3: function(M) {
        const a = M[0][0], b = M[0][1], c = M[0][2];
        const d = M[1][0], e = M[1][1], f = M[1][2];
        const g = M[2][0], h = M[2][1], i = M[2][2];
        const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
        if (Math.abs(det) < 1e-12) return null;
        const invDet = 1 / det;
        return [
            [(e * i - f * h) * invDet, (c * h - b * i) * invDet, (b * f - c * e) * invDet],
            [(f * g - d * i) * invDet, (a * i - c * g) * invDet, (c * d - a * f) * invDet],
            [(d * h - e * g) * invDet, (b * g - a * h) * invDet, (a * e - b * d) * invDet]
        ];
    },

    dampedPseudoInverse: function(J, lambda) {
        const m = 3, n = 5;

        const JJT = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
        for (let i = 0; i < m; i++) {
            for (let j = 0; j < m; j++) {
                for (let k = 0; k < n; k++) {
                    JJT[i][j] += J[i][k] * J[j][k];
                }
            }
        }

        for (let i = 0; i < m; i++) {
            JJT[i][i] += lambda * lambda;
        }

        const inv = this.invert3x3(JJT);
        if (!inv) return null;

        const Jpinv = [];
        for (let i = 0; i < n; i++) {
            Jpinv[i] = [0, 0, 0];
            for (let j = 0; j < m; j++) {
                for (let k = 0; k < m; k++) {
                    Jpinv[i][j] += J[k][i] * inv[k][j];
                }
            }
        }

        return Jpinv;
    },

    clampAngle: function(name, angleDeg) {
        const limits = this.jointLimits[name];
        if (!limits) return angleDeg;
        return Math.max(limits[0], Math.min(limits[1], angleDeg));
    },

    servoStep: function(targetPos, dt) {
        if (!targetPos || dt <= 0) return null;

        const target = targetPos instanceof THREE.Vector3
            ? targetPos
            : new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z);
        this.applyModelAngles(currentJointAngles);
        const currentPos = getEndEffectorPosition();

        const error = new THREE.Vector3().subVectors(target, currentPos);
        const errorNorm = error.length();

        if (errorNorm < 0.0015) {
            return { error: errorNorm, reached: true };
        }

        const J = this.computeJacobian(currentJointAngles);
        const Jpinv = this.dampedPseudoInverse(J, this.damping);
        if (!Jpinv) return { error: errorNorm, reached: false };

        const maxDelta = this.maxJointSpeed * dt;
        const stepGain = Math.min(0.7, Math.max(0.08, this.kp * dt));
        const stepError = error.multiplyScalar(stepGain);

        for (let i = 0; i < this.jointNames.length; i++) {
            const name = this.jointNames[i];
            const dqRad = Jpinv[i][0] * stepError.x + Jpinv[i][1] * stepError.y + Jpinv[i][2] * stepError.z;
            let deltaDeg = dqRad * 180 / Math.PI;
            deltaDeg = Math.max(-maxDelta, Math.min(maxDelta, deltaDeg));

            const newAngle = this.clampAngle(name, (currentJointAngles[name] || 0) + deltaDeg);

            currentJointAngles[name] = newAngle;

            if (jointSliders[name]) {
                jointSliders[name].value = newAngle;
                updateJointDisplay(name, newAngle);
            }

            setJointAngle(name, newAngle * Math.PI / 180);
        }

        if (robot) {
            robot.updateMatrixWorld(true);
        }
        const afterError = new THREE.Vector3().subVectors(target, getEndEffectorPosition()).length();
        return { error: afterError, reached: afterError < 0.0015 };
    }
};

function screenToWorldOnPlane(screenX, screenY, plane) {
    if (!renderer || !camera) return null;
    
    const rect = renderer.domElement.getBoundingClientRect();
    
    mouse.x = ((screenX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((screenY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);

    const intersection = new THREE.Vector3();
    
    if (plane && raycaster.ray.intersectPlane(plane, intersection)) {
        return intersection;
    }
    
    return null;
}

function createEndEffectorDragPlane() {
    const eePos = getEndEffectorPosition();
    const normal = new THREE.Vector3();
    camera.getWorldDirection(normal);
    return new THREE.Plane().setFromNormalAndCoplanarPoint(normal, eePos);
}

function screenToWorld(screenX, screenY) {
    const fixedHeight = 0.02;
    const planeY = new THREE.Plane(new THREE.Vector3(0, 1, 0), -fixedHeight);
    return screenToWorldOnPlane(screenX, screenY, planeY);
}

function startSmoothMove(newAngles) {
    if (!robot) return;
    
    targetJointAngles = { ...newAngles };
    startJointAngles = { ...currentJointAngles };
    isMovingToTarget = true;
    moveStartTime = Date.now();
    
    console.log('🎯 Starting smooth move to:', targetJointAngles);
}

function updateSmoothMove() {
    if (!isMovingToTarget) return;
    
    const elapsed = Date.now() - moveStartTime;
    const progress = Math.min(elapsed / moveDuration, 1);
    
    const easedProgress = easeInOutCubic(progress);
    
    Object.keys(targetJointAngles).forEach(jointName => {
        const startAngle = startJointAngles[jointName] || 0;
        const targetAngle = targetJointAngles[jointName];
        const currentAngle = startAngle + (targetAngle - startAngle) * easedProgress;
        
        currentJointAngles[jointName] = currentAngle;
        
        if (jointSliders[jointName]) {
            jointSliders[jointName].value = currentAngle;
            updateJointDisplay(jointName, currentAngle);
        }
        
        setJointAngle(jointName, currentAngle * Math.PI / 180);
    });
    
    if (progress >= 1) {
        isMovingToTarget = false;
        restoreOriginalMaterial();
        console.log('✅ Smooth move completed - restored original material');
    }
}

function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function setupDragInteraction() {
    const marker = document.getElementById('end-effector-marker');

    if (!marker) {
        console.warn('End effector marker not found');
        return;
    }

    console.log('✓ Setting up drag interaction (MoveIt2 servo style)');

    marker.addEventListener('mousedown', function(e) {
        if (!isDragMode) return;

        e.preventDefault();
        e.stopPropagation();
        isDraggingEndEffector = true;
        isMovingToTarget = false;
        isAnimating = false;
        marker.style.cursor = 'grabbing';
        lastServoTime = 0;
        controls.enableRotate = false;
        controls.enablePan = false;

        dragStartAngles = { ...currentJointAngles };
        dragPlane = createEndEffectorDragPlane();
        const hit = screenToWorldOnPlane(e.clientX, e.clientY, dragPlane);
        const eePos = getEndEffectorPosition();
        if (hit) {
            dragTargetWorldPos.copy(hit);
        } else {
            dragTargetWorldPos.copy(eePos);
        }

        dragGrabOffset.set(0, 0, 0);
        dragTargetActive = true;
        servoTargetPos = dragTargetWorldPos.clone();
        updateEndEffectorMarker();

        console.log('Started end-effector servo drag');
    });

    document.addEventListener('mousemove', function(e) {
        if (!isDraggingEndEffector || !isDragMode) return;

        const worldPos = screenToWorldOnPlane(e.clientX, e.clientY, dragPlane);
        if (!worldPos) return;

        dragTargetWorldPos.copy(worldPos).add(dragGrabOffset);
        servoTargetPos = dragTargetWorldPos.clone();
        updateEndEffectorMarker();

        const indicator = document.getElementById('mode-indicator');
        if (indicator) {
            indicator.textContent = `${t('targetPos')} X=${dragTargetWorldPos.x.toFixed(3)}, Y=${dragTargetWorldPos.y.toFixed(3)}, Z=${dragTargetWorldPos.z.toFixed(3)}`;
        }
    });

    document.addEventListener('mouseup', function(e) {
        if (isDraggingEndEffector) {
            isDraggingEndEffector = false;
            servoTargetPos = null;
            dragPlane = null;
            lastServoTime = 0;

            const marker = document.getElementById('end-effector-marker');
            if (marker) {
                marker.style.cursor = 'grab';
            }
            if (isDragMode) {
                controls.enableRotate = true;
                controls.enablePan = true;
            }

            restoreOriginalMaterial();

            if (dragStartAngles) {
                const targetAngles = solveIKForTarget(dragTargetWorldPos, 500, 900);

                restoreOriginalMaterial();

                Object.keys(dragStartAngles).forEach(function(jointName) {
                    currentJointAngles[jointName] = dragStartAngles[jointName];
                    if (jointSliders[jointName]) {
                        jointSliders[jointName].value = dragStartAngles[jointName];
                        updateJointDisplay(jointName, dragStartAngles[jointName]);
                    }
                    setJointAngle(jointName, dragStartAngles[jointName] * Math.PI / 180);
                });

                applyGhostMaterial();

                startJointAngles = { ...dragStartAngles };
                targetJointAngles = targetAngles;
                isMovingToTarget = true;
                moveStartTime = Date.now();
                moveDuration = 900;

                const ghostIndicator = document.getElementById('ghost-indicator');
                if (ghostIndicator) {
                    ghostIndicator.textContent = t('ghostTransition');
                }

                console.log('✋ Released - ghost transition from', startJointAngles, 'to', targetJointAngles);
            } else {
                console.log('✋ Cancelled drag, no start angles recorded');
            }

            dragStartAngles = null;
        }
    });
}
