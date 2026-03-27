import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import gsap from 'gsap';

interface AnimatedWaveform3DProps {
  isPlaying?: boolean;
}

export default function AnimatedWaveform3D({ isPlaying = false }: AnimatedWaveform3DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const waveRef = useRef<THREE.Line | null>(null);
  const timeRef = useRef(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0xfafaf9);

    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    rendererRef.current = renderer;
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);

    // Create waveform geometry
    const points: THREE.Vector3[] = [];
    const segments = 200;

    for (let i = 0; i < segments; i++) {
      const x = (i / segments) * 8 - 4;
      const y = Math.sin(i * 0.1) * 0.5;
      points.push(new THREE.Vector3(x, y, 0));
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0xa85c2a,
      linewidth: 2,
      transparent: true,
      opacity: 0.8
    });

    const wave = new THREE.Line(geometry, material);
    scene.add(wave);
    waveRef.current = wave;

    // Create tube geometry for 3D effect
    const tubePoints: THREE.Vector3[] = [];
    for (let i = 0; i < segments; i++) {
      const x = (i / segments) * 8 - 4;
      const y = Math.sin(i * 0.1) * 0.5;
      tubePoints.push(new THREE.Vector3(x, y, 0));
    }

    const curve = new THREE.CatmullRomCurve3(tubePoints);
    const tubeGeometry = new THREE.TubeGeometry(curve, 20, 0.1, 8, false);
    const tubeMaterial = new THREE.MeshPhongMaterial({
      color: 0xa85c2a,
      emissive: 0xa85c2a,
      emissiveIntensity: 0.2,
      wireframe: false,
      transparent: true,
      opacity: 0.6
    });

    const tube = new THREE.Mesh(tubeGeometry, tubeMaterial);
    scene.add(tube);

    // Lighting
    const light1 = new THREE.PointLight(0xa85c2a, 1, 100);
    light1.position.set(5, 5, 5);
    scene.add(light1);

    const light2 = new THREE.PointLight(0x3b82f6, 0.5, 100);
    light2.position.set(-5, -5, 5);
    scene.add(light2);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      if (isPlaying) {
        timeRef.current += 0.02;

        // Update waveform
        const positions = geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < segments; i++) {
          const x = (i / segments) * 8 - 4;
          const y =
            Math.sin(i * 0.1 + timeRef.current) * 0.5 +
            Math.sin(i * 0.05 + timeRef.current * 0.5) * 0.2 +
            Math.random() * 0.1;
          positions[i * 3 + 1] = y;
        }
        geometry.attributes.position.needsUpdate = true;

        // Rotate tube
        tube.rotation.z += 0.01;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
      tubeGeometry.dispose();
      tubeMaterial.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [isPlaying]);

  return (
    <div
      ref={containerRef}
      className="w-full h-48 rounded-lg border border-border overflow-hidden"
    />
  );
}
