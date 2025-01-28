import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.155.0/build/three.module.js';
import "./styles.css"

//Scene
const scene = new THREE.Scene();

//Create Sphere
const geometry = new THREE.SphereGeometry(3,64,64) 
const material = new THREE.MeshStandardMaterial({
    color : "#00ff83",
})
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)

//Sizes of viewport
const sizes = {
    width: window.innerWidth,
    height: window.innerHeight,
}

//Lights
const light = new THREE.PoitnLight(0xfffff, 1, 100)
light.position.set(0,10,10)
scene.add(camera)

//Camera
const camera = new THREE.PerspectiveCamera(45, sizes.width / sizes.height, 0.1, 100)
camera.position.z = 20  // point of view (close or far) (0.1, 100)
scene.add(camera)

//Renderer
const canves = document.querySelector(".webgl")
const renderer = new THREE.WebGLRenderer({canves})
renderer.serSize(sizes.width, sizes.height)
renderer.render(scene, camera)


//Resizing 
window.addEventListener("resize", () => {
    //Update size
    sizes.width = window.innerWidth
    sizes.height = window.innerHeight
    //Update Camera 
    camera.aspect = sizes.width / sizes.height
    camera.updateProjectionMatrix()    
    renderer.setSize(sizes.width, sizes.height)
})
// rendering every time windows resizing 
const loop = () => {
    // animation on ojects acn be added here like lights, mesh etc .. 
    renderer.render(scene, camera)
    window.requestAnimationFrame(loop)
}
loop()

