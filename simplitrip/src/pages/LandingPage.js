import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const LandingPage = () => {
    const mountRef = useRef(null);

    // useEffect hook runs the 3D animation code after the component mounts
    useEffect(() => {
        // --- THREE.JS SCENE SETUP ---
        let scene, camera, renderer, starGeo, stars;
        const mount = mountRef.current;

        const init = () => {
            // Scene
            scene = new THREE.Scene();

            // Camera
            camera = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 1, 1000);
            camera.position.z = 1;
            camera.rotation.x = Math.PI / 2;

            // Renderer
            renderer = new THREE.WebGLRenderer({
                canvas: mount.querySelector('#bg-canvas'),
                antialias: true,
            });
            renderer.setSize(mount.clientWidth, mount.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);

            // Starfield
            const starCount = 6000;
            const positions = new Float32Array(starCount * 3);
            for (let i = 0; i < starCount * 3; i++) {
                positions[i] = (Math.random() - 0.5) * 600;
            }
            starGeo = new THREE.BufferGeometry();
            starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

            let sprite = new THREE.TextureLoader().load('https://placehold.co/16x16/ffffff/ffffff.png?text=+');
            let starMaterial = new THREE.PointsMaterial({
                color: 0xaaaaaa,
                size: 0.7,
                map: sprite,
                transparent: true,
            });

            stars = new THREE.Points(starGeo, starMaterial);
            scene.add(stars);

            animate();
        };

        // --- ANIMATION LOOP ---
        const animate = () => {
            const positions = starGeo.attributes.position.array;
            for (let i = 1; i < positions.length; i += 3) {
                positions[i] -= 0.2;
                if (positions[i] < -200) {
                    positions[i] = 200;
                }
            }
            starGeo.attributes.position.needsUpdate = true;
            stars.rotation.y += 0.0002;

            renderer.render(scene, camera);
            requestAnimationFrame(animate);
        };

        // --- EVENT LISTENERS ---
        const onWindowResize = () => {
            if (mount) {
                 camera.aspect = mount.clientWidth / mount.clientHeight;
                 camera.updateProjectionMatrix();
                 renderer.setSize(mount.clientWidth, mount.clientHeight);
            }
        };
        window.addEventListener('resize', onWindowResize);
        
        init();

        // Cleanup function to remove the event listener when the component unmounts
        return () => {
            window.removeEventListener('resize', onWindowResize);
            // You might also want to dispose of Three.js objects here to free up memory
        };
    }, []); // Empty dependency array ensures this effect runs only once

    // --- SCROLL ANIMATIONS (handled with React state or Intersection Observer API) ---
    useEffect(() => {
         const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.scroll-animate').forEach(el => {
            observer.observe(el);
        });

        // Cleanup observer
        return () => observer.disconnect();
    }, []);

    // --- HEADER SCROLL EFFECT ---
    useEffect(() => {
        const header = document.querySelector('header.main-header');
        const handleScroll = () => {
            if (window.scrollY > 50) {
                header.classList.add('glass-card');
            } else {
                header.classList.remove('glass-card');
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);


    return (
        <>
            {/* We inject the custom styles directly into the component for simplicity */}
            <style>{`
                body {
                    font-family: 'Inter', sans-serif;
                    background-color: #0a0a0a;
                    color: #f0f0f0;
                    overflow-x: hidden;
                }
                #bg-canvas {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: -1;
                    opacity: 0.5;
                }
                .glass-card {
                    background: rgba(17, 24, 39, 0.6);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .scroll-animate {
                    opacity: 0;
                    transform: translateY(30px);
                    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
                }
                .scroll-animate.visible {
                    opacity: 1;
                    transform: translateY(0);
                }
            `}</style>
        
            <div ref={mountRef} className="antialiased" style={{ position: 'relative', width: '100%', height: '100%' }}>
                <canvas id="bg-canvas"></canvas>

                <header className="main-header fixed top-0 left-0 right-0 z-50 transition-all duration-300">
                    <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
                        <div className="text-2xl font-bold tracking-wider">
                            <a href="#">SimpliTrip</a>
                        </div>
                        <div className="hidden md:flex items-center space-x-8">
                            <a href="#features" className="hover:text-cyan-400 transition-colors">Features</a>
                            <a href="#about" className="hover:text-cyan-400 transition-colors">About</a>
                            <a href="#contact" className="hover:text-cyan-400 transition-colors">Contact</a>
                        </div>
                        <button className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-2 px-6 rounded-lg transition-all transform hover:scale-105">
                            Get Started
                        </button>
                    </nav>
                </header>

                <main>
                    <section className="h-screen flex items-center justify-center text-center relative">
                         <div className="z-10 px-4">
                            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter mb-4">
                                Explore the <span className="text-cyan-400">Universe</span>
                            </h1>
                            <p className="text-lg md:text-xl max-w-2xl mx-auto text-gray-300">
                                Your journey to the farthest reaches of imagination begins now. Plan, share, and experience trips like never before.
                            </p>
                            <button className="mt-8 bg-white text-black font-bold py-3 px-8 rounded-lg text-lg transform hover:scale-105 transition-transform shadow-lg-cyan">
                                Launch Your Trip
                            </button>
                        </div>
                    </section>

                    <section id="features" className="py-20 md:py-32 container mx-auto px-6">
                        <div className="text-center mb-16 scroll-animate">
                            <h2 className="text-4xl font-bold mb-2">Why Choose SimpliTrip?</h2>
                            <p className="text-gray-400">Everything you need for seamless travel planning.</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            <div className="glass-card p-8 rounded-2xl text-center scroll-animate" style={{transitionDelay: '100ms'}}>
                                <h3 className="text-2xl font-bold mb-3 text-cyan-400">3D Itinerary View</h3>
                                <p className="text-gray-300">Visualize your entire trip on an interactive 3D globe. See your path unfold in a stunning new dimension.</p>
                            </div>
                             <div className="glass-card p-8 rounded-2xl text-center scroll-animate" style={{transitionDelay: '200ms'}}>
                                <h3 className="text-2xl font-bold mb-3 text-cyan-400">Collaborative Planning</h3>
                                <p className="text-gray-300">Plan with friends and family in real-time. Share ideas, edit schedules, and build the perfect trip together.</p>
                            </div>
                            <div className="glass-card p-8 rounded-2xl text-center scroll-animate" style={{transitionDelay: '300ms'}}>
                                <h3 className="text-2xl font-bold mb-3 text-cyan-400">Smart Suggestions</h3>
                                <p className="text-gray-300">Our AI-powered assistant provides personalized recommendations for destinations, activities, and more.</p>
                            </div>
                        </div>
                    </section>
                     {/* ... Rest of the sections (About, Contact) from the HTML go here ... */}
                </main>
                
                <footer className="py-8 border-t border-gray-800 relative z-10">
                    <div className="container mx-auto px-6 text-center text-gray-500">
                        &copy; 2025 SimpliTrip. All rights reserved.
                    </div>
                </footer>
            </div>
        </>
    );
};

export default LandingPage;