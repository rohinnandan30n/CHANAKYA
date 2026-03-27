import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import gsap from 'gsap';

interface RagaNoteProps {
  raga: string | null;
}

export default function RagaNoteSphere({ raga }: RagaNoteProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sphereRef = useRef<THREE.Group | null>(null);

  const notes = ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni'];

  useEffect(() => {
    if (!containerRef.current || !raga) return;

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
    camera.position.z = 8;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    rendererRef.current = renderer;
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);

    // Create sphere group
    const sphereGroup = new THREE.Group();
    sceneRef.current.add(sphereGroup);
    sphereRef.current = sphereGroup;

    // Create central sphere
    const centralGeometry = new THREE.IcosahedronGeometry(0.5, 4);
    const centralMaterial = new THREE.MeshPhongMaterial({
      color: 0xa85c2a,
      emissive: 0xa85c2a,
      emissiveIntensity: 0.3,
      wireframe: false
    });
    const centralSphere = new THREE.Mesh(centralGeometry, centralMaterial);
    sphereGroup.add(centralSphere);

    // Add lights
    const light1 = new THREE.PointLight(0xa85c2a, 1, 100);
    light1.position.set(5, 5, 5);
    scene.add(light1);

    const light2 = new THREE.PointLight(0x3b82f6, 0.5, 100);
    light2.position.set(-5, -5, 5);
    scene.add(light2);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Create orbiting notes
    notes.forEach((note, index) => {
      const angle = (index / notes.length) * Math.PI * 2;
      const x = Math.cos(angle) * 3;
      const y = Math.sin(angle) * 3;
      const z = Math.cos(angle * 2) * 1.5;

      // Create note sphere
      const noteGeometry = new THREE.SphereGeometry(0.3, 16, 16);
      const noteMaterial = new THREE.MeshPhongMaterial({
        color: 0x3b82f6,
        emissive: 0x3b82f6,
        emissiveIntensity: 0.2
      });
      const noteSphere = new THREE.Mesh(noteGeometry, noteMaterial);
      noteSphere.position.set(x, y, z);
      sphereGroup.add(noteSphere);

      // Animate orbit
      gsap.to(noteSphere.position, {
        x: Math.cos(angle + Math.PI * 2) * 3,
        y: Math.sin(angle + Math.PI * 2) * 3,
        z: Math.cos((angle + Math.PI * 2) * 2) * 1.5,
        duration: 10 + index,
        repeat: -1,
        ease: 'none'
      });

      // Pulse animation
      gsap.to(noteSphere.scale, {
        x: 1.2,
        y: 1.2,
        z: 1.2,
        duration: 2 + index * 0.2,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    });

    // Rotate central sphere
    gsap.to(centralSphere.rotation, {
      x: Math.PI * 2,
      y: Math.PI * 2,
      duration: 12,
      repeat: -1,
      ease: 'none'
    });

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
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
      centralGeometry.dispose();
      centralMaterial.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [raga]);

  if (!raga) {
    return (
      <div className="w-full h-64 rounded-lg border border-border bg-muted flex items-center justify-center">
        <p className="text-muted-foreground">Select a Raga to visualize</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-64 rounded-lg border border-border overflow-hidden"
    />
  );
}
