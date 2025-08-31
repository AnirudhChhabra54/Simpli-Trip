import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser, loginUser } from '../services/auth';
import * as THREE from 'three';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlaneDeparture, faUser, faLock } from '@fortawesome/free-solid-svg-icons';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // --- THREE.js Scene Setup ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('three-js-container').appendChild(renderer.domElement);
        
        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        // Add directional light for shadows
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 10, 5);
        scene.add(directionalLight);

        // Create the abstract shapes
        const geometry1 = new THREE.DodecahedronGeometry(2);
        const material1 = new THREE.MeshPhongMaterial({ color: 0x00aaff, flatShading: true });
        const shape1 = new THREE.Mesh(geometry1, material1);
        shape1.position.set(-5, 0, -10);

        const geometry2 = new THREE.IcosahedronGeometry(1.5);
        const material2 = new THREE.MeshPhongMaterial({ color: 0xffaa00, flatShading: true });
        const shape2 = new THREE.Mesh(geometry2, material2);
        shape2.position.set(5, -3, -15);

        scene.add(shape1);
        scene.add(shape2);

        camera.position.z = 5;

        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            shape1.rotation.x += 0.005;
            shape1.rotation.y += 0.005;
            shape2.rotation.x -= 0.01;
            shape2.rotation.y -= 0.01;
            renderer.render(scene, camera);
        };
        animate();

        // Handle window resize
        const onWindowResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', onWindowResize);

        return () => {
            window.removeEventListener('resize', onWindowResize);
            document.getElementById('three-js-container').removeChild(renderer.domElement);
        };
    }, []);

    const handleAuth = async (isRegistering) => {
      try {
        if (isRegistering) {
          await registerUser(email, password);
          alert('Registration successful!');
        } else {
          await loginUser(email, password);
          alert('Login successful!');
        }
        navigate('/dashboard');
      } catch (error) {
        alert(error.message);
      }
    };

    return (
        <div className="relative h-screen overflow-hidden flex items-center justify-center">
            <div id="three-js-container" className="absolute top-0 left-0 w-full h-full z-0"></div>
            
            <div className="bg-white p-8 rounded-xl shadow-2xl z-10 w-96 max-w-sm">
                <div className="text-center">
                    <FontAwesomeIcon icon={faPlaneDeparture} className="text-4xl text-blue-500 mb-4" />
                    <h2 className="text-3xl font-bold text-gray-800 mb-2">Welcome to SimpliTrip</h2>
                    <p className="text-sm text-gray-600 mb-6">Plan your perfect trip with us.</p>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <input
                                type="email"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 transition-all"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="text-sm font-medium text-gray-700">Password</label>
                        <div className="mt-1 relative rounded-md shadow-sm">
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 transition-all"
                            />
                        </div>
                    </div>

                    <div className="flex flex-col space-y-2">
                        <button
                            onClick={() => handleAuth(false)}
                            className="w-full bg-blue-600 text-white py-2 rounded-md font-semibold hover:bg-blue-700 transition-colors"
                        >
                            Login
                        </button>
                        <button
                            onClick={() => handleAuth(true)}
                            className="w-full bg-gray-200 text-gray-800 py-2 rounded-md font-semibold hover:bg-gray-300 transition-colors"
                        >
                            Register
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;