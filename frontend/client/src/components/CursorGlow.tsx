import { useEffect, useRef } from 'react';

export default function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const posRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Smooth animation loop for glow following
    const animate = () => {
      if (glowRef.current) {
        // Smooth interpolation for trailing effect
        posRef.current.x += (mouseRef.current.x - posRef.current.x) * 0.1;
        posRef.current.y += (mouseRef.current.y - posRef.current.y) * 0.1;

        glowRef.current.style.left = posRef.current.x + 'px';
        glowRef.current.style.top = posRef.current.y + 'px';
      }
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div
      ref={glowRef}
      className="fixed pointer-events-none z-50"
      style={{
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255, 180, 100, 0.6) 0%, rgba(255, 140, 60, 0.3) 50%, rgba(255, 100, 20, 0) 100%)',
        boxShadow: `
          0 0 20px rgba(255, 180, 100, 0.5),
          0 0 40px rgba(255, 140, 60, 0.3),
          inset 0 0 20px rgba(255, 200, 120, 0.4)
        `,
        filter: 'blur(1px)',
        transform: 'translate(-50%, -50%)',
        mixBlendMode: 'screen',
      }}
    />
  );
}
