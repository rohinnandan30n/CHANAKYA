import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import gsap from 'gsap';

export default function DivineSpaceHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const particlesRef = useRef<THREE.Points | null>(null);
  const glitterRef = useRef<THREE.Points | null>(null);
  const timeRef = useRef(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup with cosmic background
    const scene = new THREE.Scene();
    sceneRef.current = scene;

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

    // Create gradient background with canvas
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      const gradient = ctx.createLinearGradient(0, 0, 512, 512);
      gradient.addColorStop(0, '#0a0e27'); // Deep space blue
      gradient.addColorStop(0.25, '#1a1a4d'); // Purple
      gradient.addColorStop(0.5, '#2d1b4e'); // Deep purple
      gradient.addColorStop(0.75, '#1a1a3d'); // Blue-purple
      gradient.addColorStop(1, '#0f0f2e'); // Dark blue
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 512, 512);
    }

    const texture = new THREE.CanvasTexture(canvas);
    scene.background = texture;

    // Create smooth flowing particles (cosmic dust)
    const particleCount = 800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 30;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 30;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

      // Cosmic colors: golds, purples, blues
      const colorChoice = Math.random();
      if (colorChoice < 0.33) {
        colors[i * 3] = 1; // Gold
        colors[i * 3 + 1] = 0.8;
        colors[i * 3 + 2] = 0.2;
      } else if (colorChoice < 0.66) {
        colors[i * 3] = 0.8; // Purple
        colors[i * 3 + 1] = 0.4;
        colors[i * 3 + 2] = 1;
      } else {
        colors[i * 3] = 0.4; // Cyan
        colors[i * 3 + 1] = 0.8;
        colors[i * 3 + 2] = 1;
      }

      sizes[i] = Math.random() * 0.3 + 0.1;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 3));

    const material = new THREE.PointsMaterial({
      size: 0.15,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      fog: false,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
    particlesRef.current = particles;

    // Create glitter particles that respond to mouse
    const glitterCount = 200;
    const glitterGeometry = new THREE.BufferGeometry();
    const glitterPositions = new Float32Array(glitterCount * 3);
    const glitterColors = new Float32Array(glitterCount * 3);
    const glitterSizes = new Float32Array(glitterCount);

    for (let i = 0; i < glitterCount; i++) {
      glitterPositions[i * 3] = (Math.random() - 0.5) * 30;
      glitterPositions[i * 3 + 1] = (Math.random() - 0.5) * 30;
      glitterPositions[i * 3 + 2] = (Math.random() - 0.5) * 20;

      // Bright glittery colors
      glitterColors[i * 3] = 1;
      glitterColors[i * 3 + 1] = 1;
      glitterColors[i * 3 + 2] = 1;

      glitterSizes[i] = Math.random() * 0.2 + 0.05;
    }

    glitterGeometry.setAttribute('position', new THREE.BufferAttribute(glitterPositions, 3));
    glitterGeometry.setAttribute('color', new THREE.BufferAttribute(glitterColors, 3));
    glitterGeometry.setAttribute('size', new THREE.BufferAttribute(glitterSizes, 3));

    const glitterMaterial = new THREE.PointsMaterial({
      size: 0.2,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0,
      fog: false,
    });

    const glitter = new THREE.Points(glitterGeometry, glitterMaterial);
    scene.add(glitter);
    glitterRef.current = glitter;

    // Lighting - divine glow
    const light1 = new THREE.PointLight(0xffd700, 1.5, 100);
    light1.position.set(10, 10, 10);
    scene.add(light1);

    const light2 = new THREE.PointLight(0x8b5cf6, 1, 100);
    light2.position.set(-10, -10, 10);
    scene.add(light2);

    const light3 = new THREE.PointLight(0x06b6d4, 0.8, 100);
    light3.position.set(0, 0, 15);
    scene.add(light3);

    // Mouse tracking
    const handleMouseMove = (event: MouseEvent) => {
      if (!containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Create glitter burst at mouse position
      if (glitterRef.current && glitterMaterial) {
        gsap.to(glitterMaterial, {
          opacity: 0.8,
          duration: 0.1,
          onComplete: () => {
            gsap.to(glitterMaterial, {
              opacity: 0,
              duration: 0.5,
              ease: 'power2.out',
            });
          },
        });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Smooth particle animation
    gsap.to(particles.rotation, {
      x: Math.PI * 0.5,
      y: Math.PI * 0.5,
      duration: 30,
      repeat: -1,
      ease: 'none',
    });

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      timeRef.current += 0.001;

      // Update particle positions for smooth flow
      const positionArray = geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        positionArray[i3 + 1] += Math.sin(timeRef.current + i) * 0.001;
        positionArray[i3] += Math.cos(timeRef.current + i * 0.5) * 0.0005;
      }
      geometry.attributes.position.needsUpdate = true;

      // Move glitter towards mouse
      if (glitterRef.current) {
        const glitterPosArray = glitterGeometry.attributes.position.array as Float32Array;
        for (let i = 0; i < glitterCount; i++) {
          const i3 = i * 3;
          const targetX = mouseRef.current.x * 15;
          const targetY = mouseRef.current.y * 15;

          glitterPosArray[i3] += (targetX - glitterPosArray[i3]) * 0.05;
          glitterPosArray[i3 + 1] += (targetY - glitterPosArray[i3 + 1]) * 0.05;
        }
        glitterGeometry.attributes.position.needsUpdate = true;
      }

      // Gentle camera movement
      camera.position.x = Math.sin(timeRef.current * 0.2) * 1;
      camera.position.y = Math.cos(timeRef.current * 0.15) * 1;
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
      window.removeEventListener('mousemove', handleMouseMove);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
      glitterGeometry.dispose();
      glitterMaterial.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full cursor-crosshair"
      style={{ pointerEvents: 'none' }}
    />
  );
}
