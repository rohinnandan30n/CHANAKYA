import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import gsap from 'gsap';

const MANTRAS = [
  { text: 'ॐ', meaning: 'Om - The primordial sound', color: 0xa85c2a },
  { text: 'नमस्ते', meaning: 'Namaste - I bow to you', color: 0xd97706 },
  { text: 'शान्तिः', meaning: 'Shanti - Peace', color: 0xf59e0b },
  { text: 'सत्यम्', meaning: 'Satya - Truth', color: 0xfbbf24 },
];

export default function MantrasHeroAnimation() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const timeRef = useRef(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0xfefce8);
    scene.fog = new THREE.Fog(0xfefce8, 15, 30);

    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 8;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    rendererRef.current = renderer;
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    containerRef.current.appendChild(renderer.domElement);

    // Create flowing particle system representing mantras
    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const velocities = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const x = (Math.random() - 0.5) * 20;
      const y = (Math.random() - 0.5) * 20;
      const z = (Math.random() - 0.5) * 10;

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      // Color based on mantra energy
      const mantra = MANTRAS[Math.floor(Math.random() * MANTRAS.length)];
      const color = new THREE.Color(mantra.color);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;

      sizes[i] = Math.random() * 0.15 + 0.05;

      velocities[i * 3] = (Math.random() - 0.5) * 0.02;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.PointsMaterial({
      size: 0.1,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      fog: true,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
    particlesRef.current = particles;

    // Create flowing ripple effect (fluid dynamics)
    const rippleGeometry = new THREE.IcosahedronGeometry(2, 6);
    const rippleMaterial = new THREE.MeshPhongMaterial({
      color: 0xa85c2a,
      emissive: 0xa85c2a,
      emissiveIntensity: 0.1,
      wireframe: true,
      transparent: true,
      opacity: 0.2,
    });
    const rippleMesh = new THREE.Mesh(rippleGeometry, rippleMaterial);
    scene.add(rippleMesh);

    // Create multiple ripple layers for depth
    const rippleLayers: THREE.Mesh[] = [];
    for (let i = 0; i < 3; i++) {
      const layerGeometry = new THREE.IcosahedronGeometry(2 + i * 0.5, 5);
      const layerMaterial = new THREE.MeshPhongMaterial({
        color: new THREE.Color(MANTRAS[i % MANTRAS.length].color),
        emissive: new THREE.Color(MANTRAS[i % MANTRAS.length].color),
        emissiveIntensity: 0.05,
        wireframe: true,
        transparent: true,
        opacity: 0.15 - i * 0.03,
      });
      const layerMesh = new THREE.Mesh(layerGeometry, layerMaterial);
      scene.add(layerMesh);
      rippleLayers.push(layerMesh);
    }

    // Lighting - ethereal glow effect
    const light1 = new THREE.PointLight(0xa85c2a, 2, 50);
    light1.position.set(5, 5, 5);
    light1.castShadow = true;
    scene.add(light1);

    const light2 = new THREE.PointLight(0xd97706, 1.5, 50);
    light2.position.set(-5, -5, 5);
    scene.add(light2);

    const light3 = new THREE.PointLight(0xf59e0b, 1, 40);
    light3.position.set(0, 0, 8);
    scene.add(light3);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    scene.add(ambientLight);

    // Animate ripple layers with pulsing effect
    rippleLayers.forEach((layer, index) => {
      gsap.to(layer.rotation, {
        x: Math.PI * 2,
        y: Math.PI * 2,
        duration: 15 + index * 5,
        repeat: -1,
        ease: 'none',
      });

      gsap.to(layer.scale, {
        x: 1 + Math.sin(index) * 0.3,
        y: 1 + Math.sin(index) * 0.3,
        z: 1 + Math.sin(index) * 0.3,
        duration: 4 + index,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      });
    });

    // Animate lights with pulsing effect
    gsap.to(light1, {
      intensity: 2.5,
      duration: 3,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    });

    gsap.to(light2, {
      intensity: 2,
      duration: 4,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    });

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      timeRef.current += 0.001;

      // Update particle positions for fluid flow
      const positionArray = geometry.attributes.position.array as Float32Array;
      const velocityArray = velocities;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;

        // Apply velocity
        positionArray[i3] += velocityArray[i3];
        positionArray[i3 + 1] += velocityArray[i3 + 1];
        positionArray[i3 + 2] += velocityArray[i3 + 2];

        // Add wave motion (fluid dynamics)
        const wave =
          Math.sin(positionArray[i3] * 0.5 + timeRef.current) * 0.01 +
          Math.cos(positionArray[i3 + 1] * 0.5 + timeRef.current) * 0.01;
        positionArray[i3 + 1] += wave;

        // Wrap around boundaries
        if (Math.abs(positionArray[i3]) > 10) velocityArray[i3] *= -1;
        if (Math.abs(positionArray[i3 + 1]) > 10) velocityArray[i3 + 1] *= -1;
        if (Math.abs(positionArray[i3 + 2]) > 5) velocityArray[i3 + 2] *= -1;
      }

      geometry.attributes.position.needsUpdate = true;

      // Gentle camera movement
      camera.position.x = Math.sin(timeRef.current * 0.3) * 2;
      camera.position.y = Math.cos(timeRef.current * 0.2) * 1.5;
      camera.lookAt(0, 0, 0);

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
      rippleLayers.forEach((layer) => {
        layer.geometry.dispose();
        (layer.material as THREE.Material).dispose();
      });
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full"
      style={{ pointerEvents: 'none' }}
    />
  );
}
