import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser, loginUser } from '../services/auth';
import * as THREE from 'three';

// A simple SVG icon for a hand-drawn paper plane
const PaperPlaneIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
);

// Decorative SVG "doodle" elements
const Doodle = ({ className }) => (
    <svg className={`absolute ${className} text-gray-300`} width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 10 C 20 20, 40 20, 50 10 S 70 0, 90 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M10 30 C 20 40, 40 40, 50 30 S 70 20, 90 30" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M10 50 C 20 60, 40 60, 50 50 S 70 40, 90 50" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
);


const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const mountRef = useRef(null);

    useEffect(() => {
        const currentMount = mountRef.current;
        if (!currentMount) return;

        // --- THREE.js Scene Setup ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, currentMount.clientWidth / currentMount.clientHeight, 0.1, 1000);
        camera.position.z = 20;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
        currentMount.appendChild(renderer.domElement);

        // --- Sketchy Paper Plane ---
        const planePoints = [
            new THREE.Vector3(0, 0, 0), new THREE.Vector3(3, 1, 0),
            new THREE.Vector3(0, 0, 0), new THREE.Vector3(-3, 1, 0),
            new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 5),
            new THREE.Vector3(3, 1, 0), new THREE.Vector3(0, 0, 5),
            new THREE.Vector3(-3, 1, 0), new THREE.Vector3(0, 0, 5),
            new THREE.Vector3(3, 1, 0), new THREE.Vector3(-3, 1, 0),
        ];
        
        const planeGeometry = new THREE.BufferGeometry().setFromPoints(planePoints);
        const planeMaterial = new THREE.LineBasicMaterial({ color: 0x4a5568 }); // Gray-700
        const paperPlane = new THREE.LineSegments(planeGeometry, planeMaterial);
        scene.add(paperPlane);

        // --- Animation Loop ---
        const clock = new THREE.Clock();
        const animate = () => {
            requestAnimationFrame(animate);
            const elapsedTime = clock.getElapsedTime();

            // Animate plane in a figure-eight path
            paperPlane.position.x = Math.sin(elapsedTime * 0.5) * 10;
            paperPlane.position.y = Math.cos(elapsedTime * 0.3) * 5;
            paperPlane.rotation.y = elapsedTime * 0.2;
            paperPlane.rotation.x = elapsedTime * 0.1;
            
            renderer.render(scene, camera);
        };
        animate();

        // --- Event Listeners ---
        const onWindowResize = () => {
            camera.aspect = currentMount.clientWidth / currentMount.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
        };
        window.addEventListener('resize', onWindowResize);

        // --- Cleanup ---
        return () => {
            window.removeEventListener('resize', onWindowResize);
            if (currentMount) {
                currentMount.removeChild(renderer.domElement);
            }
        };
    }, []);

    const handleAuth = async (isRegistering) => {
        try {
            if (isRegistering) {
                await registerUser(email, password);
                alert('Registration successful! Please log in.');
            } else {
                await loginUser(email, password);
                // Auth context will handle navigation
            }
        } catch (error) {
            alert(error.message);
        }
    };

    return (
        <>
            {/* Injecting a playful, handwritten font */}
            <style jsx global>{`
                @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap');
                .font-kalam { font-family: 'Kalam', cursive; }
            `}</style>
            
            <div className="min-h-screen bg-[#F7F5F2] font-sans flex items-center justify-center overflow-hidden">
                <Doodle className="top-10 left-10 transform rotate-12" />
                <Doodle className="bottom-10 right-10 transform -rotate-12" />

                <main className="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full max-w-6xl mx-auto">
                    {/* Left side: 3D Animation */}
                    <div className="hidden lg:flex items-center justify-center h-[500px]">
                        <div ref={mountRef} className="w-full h-full"></div>
                    </div>

                    {/* Right side: Login Form */}
                    <div className="flex items-center justify-center p-8">
                        <div className="w-full max-w-sm p-8 space-y-6 bg-white border-2 border-gray-800 rounded-lg shadow-[8px_8px_0px_#4a5568]">
                            <div className="text-center">
                                <PaperPlaneIcon />
                                <h2 className="text-4xl font-bold font-kalam text-gray-800 mt-2">SimpliTrip</h2>
                                <p className="text-gray-600">Let's sketch out your next adventure.</p>
                            </div>

                            <form className="space-y-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Email</label>
                                    <input
                                        type="email"
                                        placeholder="your.email@fly.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full px-4 py-2 bg-white border-2 border-gray-400 rounded-md focus:outline-none focus:border-gray-800 focus:ring-0 transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Password</label>
                                    <input
                                        type="password"
                                        placeholder="Your secret passphrase"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full px-4 py-2 bg-white border-2 border-gray-400 rounded-md focus:outline-none focus:border-gray-800 focus:ring-0 transition-all"
                                    />
                                </div>
                                <div className="flex flex-col space-y-3 pt-4">
                                    <button
                                        type="button"
                                        onClick={() => handleAuth(false)}
                                        className="w-full bg-blue-500 text-white py-2.5 rounded-md font-bold border-2 border-blue-700 hover:bg-blue-600 transition-all transform hover:-translate-y-0.5"
                                    >
                                        Login
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => handleAuth(true)}
                                        className="w-full bg-gray-200 text-gray-800 py-2.5 rounded-md font-bold border-2 border-gray-400 hover:bg-gray-300 transition-all"
                                    >
                                        Register
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </main>
            </div>
        </>
    );
};

export default LoginPage;

