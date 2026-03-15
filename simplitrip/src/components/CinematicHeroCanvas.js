import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const CinematicHeroCanvas = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    const width = currentMount.clientWidth || window.innerWidth;
    const height = currentMount.clientHeight || window.innerHeight;

    // 1. Scene & Camera Setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 240;

    // 2. WebGL Renderer
    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    // 3. Globe Container Group (for combined rotation & mouse tilt)
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // Subtle offset towards the right on desktop for cinematic text balance
    globeGroup.position.set(30, 0, 0);

    // 3a. Inner Glowing Core Sphere
    const coreGeometry = new THREE.SphereGeometry(60, 36, 36);
    const coreMaterial = new THREE.MeshBasicMaterial({
      color: 0x051329,
      transparent: true,
      opacity: 0.85,
    });
    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    globeGroup.add(coreMesh);

    // 3b. Wireframe Outer Atmosphere Grid
    const wireframeGeometry = new THREE.SphereGeometry(62, 28, 28);
    const wireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      wireframe: true,
      transparent: true,
      opacity: 0.15,
    });
    const wireframeMesh = new THREE.Mesh(wireframeGeometry, wireframeMaterial);
    globeGroup.add(wireframeMesh);

    // 3c. Globe Surface Dots / Constellation Points
    const dotCount = 900;
    const dotGeometry = new THREE.BufferGeometry();
    const dotPositions = new Float32Array(dotCount * 3);
    const radius = 62;

    for (let i = 0; i < dotCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / dotCount);
      const theta = Math.sqrt(dotCount * Math.PI) * phi;

      const x = radius * Math.cos(theta) * Math.sin(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(phi);

      dotPositions[i * 3] = x;
      dotPositions[i * 3 + 1] = y;
      dotPositions[i * 3 + 2] = z;
    }

    dotGeometry.setAttribute('position', new THREE.BufferAttribute(dotPositions, 3));
    const dotMaterial = new THREE.PointsMaterial({
      color: 0x38bdf8,
      size: 1.2,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
    });
    const dotPoints = new THREE.Points(dotGeometry, dotMaterial);
    globeGroup.add(dotPoints);

    // 4. Destination Beacons & Glowing Flight Path Arcs
    // Key latitude/longitude coordinates mapped to 3D sphere
    const latLngToVector3 = (lat, lng, r) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lng + 180) * (Math.PI / 180);
      return new THREE.Vector3(
        -r * Math.sin(phi) * Math.cos(theta),
        r * Math.cos(phi),
        r * Math.sin(phi) * Math.sin(theta)
      );
    };

    const hubs = [
      { name: 'Goa / Mumbai', lat: 19.07, lng: 72.87 },
      { name: 'Delhi / Ladakh', lat: 34.15, lng: 77.57 },
      { name: 'Tokyo', lat: 35.67, lng: 139.65 },
      { name: 'Paris / Alps', lat: 48.85, lng: 2.35 },
      { name: 'New York', lat: 40.71, lng: -74.0 },
      { name: 'Bali', lat: -8.4, lng: 115.18 },
      { name: 'Dubai', lat: 25.2, lng: 55.27 },
      { name: 'London', lat: 51.5, lng: -0.12 },
    ];

    // Add beacon markers
    hubs.forEach((hub) => {
      const pos = latLngToVector3(hub.lat, hub.lng, 63);
      const markerGeo = new THREE.SphereGeometry(1.4, 12, 12);
      const markerMat = new THREE.MeshBasicMaterial({
        color: 0x22d3ee,
        blending: THREE.AdditiveBlending,
      });
      const marker = new THREE.Mesh(markerGeo, markerMat);
      marker.position.copy(pos);
      globeGroup.add(marker);

      // Outer ripple ring
      const ringGeo = new THREE.RingGeometry(1.6, 2.4, 16);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x06b6d4,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.copy(pos);
      ring.lookAt(new THREE.Vector3(0, 0, 0));
      globeGroup.add(ring);
    });

    // Create Curved Flight Arcs between major hubs
    const routes = [
      [0, 1], // Mumbai -> Ladakh
      [0, 6], // Mumbai -> Dubai
      [6, 3], // Dubai -> Paris
      [3, 7], // Paris -> London
      [7, 4], // London -> NY
      [0, 5], // Mumbai -> Bali
      [5, 2], // Bali -> Tokyo
    ];

    routes.forEach(([srcIdx, dstIdx]) => {
      const p1 = latLngToVector3(hubs[srcIdx].lat, hubs[srcIdx].lng, 62.5);
      const p2 = latLngToVector3(hubs[dstIdx].lat, hubs[dstIdx].lng, 62.5);

      // Midpoint elevated away from sphere center to create arc
      const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
      const distance = p1.distanceTo(p2);
      mid.normalize().multiplyScalar(62.5 + distance * 0.22);

      const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2);
      const points = curve.getPoints(40);
      const arcGeometry = new THREE.BufferGeometry().setFromPoints(points);

      const arcMaterial = new THREE.LineBasicMaterial({
        color: 0xa855f7,
        transparent: true,
        opacity: 0.45,
        linewidth: 1,
        blending: THREE.AdditiveBlending,
      });

      const arcLine = new THREE.Line(arcGeometry, arcMaterial);
      globeGroup.add(arcLine);
    });

    // 5. Ambient Stardust Galaxy (Stars Background)
    const starCount = 600;
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount; i++) {
      starPositions[i * 3] = (Math.random() - 0.5) * 450;
      starPositions[i * 3 + 1] = (Math.random() - 0.5) * 350;
      starPositions[i * 3 + 2] = (Math.random() - 0.5) * 350 - 30;

      // Color variation: Ice Cyan, Lavender, Gold, White
      const colorChoice = Math.random();
      if (colorChoice < 0.4) {
        // Cyan
        starColors[i * 3] = 0.2;
        starColors[i * 3 + 1] = 0.8;
        starColors[i * 3 + 2] = 1.0;
      } else if (colorChoice < 0.7) {
        // Violet / Purple
        starColors[i * 3] = 0.7;
        starColors[i * 3 + 1] = 0.4;
        starColors[i * 3 + 2] = 1.0;
      } else {
        // Soft White / Gold
        starColors[i * 3] = 0.95;
        starColors[i * 3 + 1] = 0.95;
        starColors[i * 3 + 2] = 1.0;
      }
    }

    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    starGeometry.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

    const starMaterial = new THREE.PointsMaterial({
      size: 1.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });
    const starField = new THREE.Points(starGeometry, starMaterial);
    scene.add(starField);

    // 6. Interactive Mouse & Gyro Coordinates
    let targetRotationX = 0.2;
    let targetRotationY = 0;

    const onMouseMove = (event) => {
      const mouseX = (event.clientX / window.innerWidth) * 2 - 1;
      const mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

      targetRotationY = mouseX * 0.4;
      targetRotationX = mouseY * 0.3;
    };

    window.addEventListener('mousemove', onMouseMove, { passive: true });

    // 7. Responsive Resize Listener
    const onWindowResize = () => {
      if (!currentMount) return;
      const newWidth = currentMount.clientWidth || window.innerWidth;
      const newHeight = currentMount.clientHeight || window.innerHeight;

      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);

      // Adjust globe position based on screen width
      if (newWidth < 768) {
        globeGroup.position.set(0, 15, -20);
        camera.position.z = 260;
      } else {
        globeGroup.position.set(38, 0, 0);
        camera.position.z = 230;
      }
    };

    window.addEventListener('resize', onWindowResize);
    onWindowResize(); // initial check

    // 8. Animation Render Loop
    let animationFrameId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Continuous slow celestial rotation
      globeGroup.rotation.y += 0.0022;

      // Smooth inertia interpolation towards mouse target
      globeGroup.rotation.x += (targetRotationX - globeGroup.rotation.x) * 0.03;
      globeGroup.rotation.z += (targetRotationY * 0.2 - globeGroup.rotation.z) * 0.03;
      globeGroup.position.y = Math.sin(elapsedTime * 0.8) * 3; // subtle breathing float

      // Slow starfield drift
      starField.rotation.y = elapsedTime * 0.0004;
      starField.rotation.x = elapsedTime * 0.0002;

      // Pulse wireframe opacity gently
      wireframeMaterial.opacity = 0.14 + Math.sin(elapsedTime * 1.5) * 0.04;

      renderer.render(scene, camera);
    };

    animate();

    // 9. Clean up on unmount
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onWindowResize);
      cancelAnimationFrame(animationFrameId);

      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }

      // Dispose geometries & materials
      coreGeometry.dispose();
      coreMaterial.dispose();
      wireframeGeometry.dispose();
      wireframeMaterial.dispose();
      dotGeometry.dispose();
      dotMaterial.dispose();
      starGeometry.dispose();
      starMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="absolute inset-0 pointer-events-none z-0 overflow-hidden w-full h-full"
      style={{ opacity: 0.95 }}
    />
  );
};

export default CinematicHeroCanvas;
