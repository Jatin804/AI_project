import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.172.0/build/three.module.js';

document.addEventListener('DOMContentLoaded', () => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
    const renderer = new THREE.WebGLRenderer();

    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Create a sphere
    let geometry = new THREE.SphereGeometry(1, 128, 128);
    let material = new THREE.MeshBasicMaterial({ color: 0x0077ff, wireframe: true });
    let sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);
    camera.position.z = 5;

    function animate() {
        requestAnimationFrame(animate);
        sphere.rotation.x += 0.01;
        sphere.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();

    // Function to fetch speech from Django when the button is clicked
    function fetchSpeechData() {
        fetch('call_fetch')
            .then(response => response.json())
            .then(data => {
                console.log("AI Response:", data.text);
                updateSphereSize(data.loudness);
                speakText(data.text);
            })
            .catch(error => console.error("Error fetching speech data:", error));
    }

    function updateSphereSize(loudness) {
        let scale = Math.min(2, Math.max(0.5, loudness / 100)); // Keep size in range
        sphere.scale.set(scale, scale, scale);
    }

    function speakText(text) {
        let utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    }

    // Add event listener to the button to trigger speech recognition
    document.getElementById("start-chat").addEventListener("click", fetchSpeechData);
});
