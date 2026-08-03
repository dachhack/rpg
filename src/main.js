import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const container = document.querySelector('#app');

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0e0e12);

// Camera
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(3, 2, 5);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lights
const ambient = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambient);

const directional = new THREE.DirectionalLight(0xffffff, 1.2);
directional.position.set(5, 5, 5);
scene.add(directional);

// Ground grid for orientation
const grid = new THREE.GridHelper(10, 10, 0x444455, 0x26262e);
scene.add(grid);

// Placeholder animated object: a spinning cube
const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x4f8ff7, roughness: 0.35 })
);
cube.position.y = 0.5;
scene.add(cube);

// Handle resizing
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
const clock = new THREE.Clock();

function animate() {
  const elapsed = clock.getElapsedTime();

  cube.rotation.y = elapsed;
  cube.rotation.x = elapsed * 0.5;
  cube.position.y = 0.5 + Math.sin(elapsed * 2) * 0.25;

  controls.update();
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
