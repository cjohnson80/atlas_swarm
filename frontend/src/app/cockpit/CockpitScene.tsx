"use client";

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Float, Text, MeshDistortMaterial, PerspectiveCamera } from '@react-three/drei';

const SwarmNode = ({ position, label, color = "#00d2ff" }: { position: [number, number, number], label: string, color?: string }) => {
  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <mesh position={position}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <MeshDistortMaterial
          color={color}
          speed={3}
          distort={0.4}
          radius={1}
        />
        <Text
          position={[0, 1.2, 0]}
          fontSize={0.3}
          color="white"
          anchorX="center"
          anchorY="middle"
          font="/fonts/Inter-Bold.woff" // Assuming standard font path
        >
          {label}
        </Text>
      </mesh>
    </Float>
  );
};

const DataStreams = () => {
  return (
    <group>
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <gridHelper args={[100, 50, "#333", "#111"]} position={[0, -5, 0]} />
    </group>
  );
};

export default function CockpitScene() {
  return (
    <div className="w-full h-screen bg-[#050505]">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[0, 5, 15]} fov={50} />
        <color attach="background" args={['#050505']} />
        
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, 20, 10]} angle={0.15} penumbra={1} intensity={2} castShadow />

        <Suspense fallback={null}>
          <DataStreams />
          
          {/* Central Core */}
          <SwarmNode position={[0, 0, 0]} label="ATLAS_CORE" color="#00ffcc" />
          
          {/* Specialized Expert Nodes */}
          <SwarmNode position={[-5, 2, -3]} label="ARCHITECT" />
          <SwarmNode position={[5, 2, -3]} label="SECURITY" color="#ff0055" />
          <SwarmNode position={[-4, -2, 4]} label="DEVELOPER" color="#aa00ff" />
          <SwarmNode position={[4, -2, 4]} label="DATABASE" color="#ffaa00" />
          
          <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
        </Suspense>
      </Canvas>
      
      <div className="absolute top-10 left-10 text-white font-mono pointer-events-none">
        <h1 className="text-4xl font-bold tracking-tighter text-[#00d2ff]">ATLAS_COCKPIT v1.0</h1>
        <p className="text-sm opacity-50 uppercase tracking-widest">Spatial Swarm Monitoring Active</p>
      </div>
    </div>
  );
}
