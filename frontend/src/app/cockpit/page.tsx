"use client";

import React, { Suspense, useState, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { 
  OrbitControls, 
  PerspectiveCamera, 
  Stars, 
  Float, 
  Text,
  MeshDistortMaterial,
  Environment,
  ContactShadows,
  Line,
  Html
} from "@react-three/drei";
import * as THREE from "three";
import { 
  BrainCircuit, 
  Zap, 
  Shield, 
  Terminal, 
  Cpu, 
  Layers,
  Search,
  Settings,
  Bell,
  User,
  Command,
  Play,
  Box,
  Eye
} from "lucide-react";

// --- Components ---

function CodingNode({ position, title, color, active = false }: { position: [number, number, number], title: string, color: string, active?: boolean }) {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (active && meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.5;
    }
  });

  return (
    <Float speed={active ? 4 : 2} rotationIntensity={active ? 1 : 0.5} floatIntensity={1}>
      <group position={position} onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
        <mesh ref={meshRef}>
          <boxGeometry args={[1.8, 1.2, 0.2]} />
          <MeshDistortMaterial 
            color={hovered || active ? "#4f46e5" : color} 
            speed={active ? 4 : 2} 
            distort={active ? 0.4 : 0.2} 
            radius={1}
            emissive={hovered || active ? "#4f46e5" : "#000"}
            emissiveIntensity={active ? 0.8 : 0.3}
            wireframe={active}
          />
        </mesh>
        <Text
          position={[0, 0, 0.15]}
          fontSize={0.18}
          color="white"
          anchorX="center"
          anchorY="middle"
          font="https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff"
        >
          {title}
        </Text>
        {active && (
          <Text position={[0, -0.8, 0]} fontSize={0.1} color="#34d399">
            [Swarm Active]
          </Text>
        )}
      </group>
    </Float>
  );
}

function ConnectionLine({ start, end }: { start: [number, number, number], end: [number, number, number] }) {
  const points = useMemo(() => [new THREE.Vector3(...start), new THREE.Vector3(...end)], [start, end]);
  return (
    <Line points={points} color="#3b82f6" lineWidth={2} dashed dashScale={20} dashSize={1} dashOffset={0} opacity={0.3} transparent />
  );
}

function InfiniteGrid() {
  return (
    <gridHelper args={[100, 100, "#1e1e1e", "#121212"]} position={[0, -3, 0]} />
  );
}

function HolographicPreview({ position }: { position: [number, number, number] }) {
  return (
    <Float speed={1} rotationIntensity={0.2} floatIntensity={0.5}>
      <group position={position}>
        <mesh>
          <planeGeometry args={[4, 3]} />
          <meshBasicMaterial color="#000" opacity={0.8} transparent side={THREE.DoubleSide} />
        </mesh>
        <Html transform distanceFactor={5} position={[0, 0, 0.01]}>
          <div className="w-[800px] h-[600px] bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden flex flex-col pointer-events-none">
            <div className="h-10 bg-zinc-900 border-b border-zinc-800 flex items-center px-4 gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-4 text-xs font-mono text-zinc-500">localhost:3000 (Live WebContainer)</span>
            </div>
            <div className="flex-1 flex items-center justify-center p-8 bg-black">
               <div className="text-center space-y-4">
                  <div className="inline-block p-4 rounded-full bg-blue-500/10 border border-blue-500/20 animate-pulse">
                    <Zap className="w-8 h-8 text-blue-500" />
                  </div>
                  <h3 className="text-white font-bold tracking-tight">App Rendering...</h3>
               </div>
            </div>
          </div>
        </Html>
      </group>
    </Float>
  );
}

function CockpitScene({ astData }: { astData: any }) {
  const nodePositions = {
    core: [0, 1, -2] as [number, number, number],
    frontend: [-5, 2, 0] as [number, number, number],
    backend: [5, 1.5, 0] as [number, number, number],
    database: [0, 3, -6] as [number, number, number]
  };

  const dynamicNodes = useMemo(() => {
    if (!astData) return null;
    const items = Object.keys(astData);
    return items.map((key, i) => {
      const angle = (i / items.length) * Math.PI * 2;
      const radius = 8 + (i % 3); // stagger radius
      return {
        id: key,
        title: key.split('/').pop() || key,
        position: [Math.cos(angle) * radius, (Math.random() * 6) - 3, Math.sin(angle) * radius] as [number, number, number],
        color: "#1e293b",
        active: Math.random() > 0.8
      };
    });
  }, [astData]);

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 5, 12]} fov={55} />
      <OrbitControls makeDefault enablePan={true} enableZoom={true} />
      
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1.5} color="#4f46e5" />
      <spotLight position={[-10, 10, 10]} angle={0.2} penumbra={1} intensity={2} castShadow />
      
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <InfiniteGrid />
      
      {/* Central Swarm Core */}
      <Float speed={4} rotationIntensity={3} floatIntensity={2}>
        <mesh position={[0, 0, 0]}>
          <octahedronGeometry args={[1.2, 0]} />
          <meshStandardMaterial color="#3b82f6" wireframe />
        </mesh>
      </Float>

      {/* AST Nodes */}
      {dynamicNodes ? dynamicNodes.map((node) => (
        <React.Fragment key={node.id}>
          <CodingNode position={node.position} title={node.title} color={node.color} active={node.active} />
          <ConnectionLine start={node.position} end={[0, 0, 0]} />
        </React.Fragment>
      )) : (
        <>
          <CodingNode position={nodePositions.frontend} title="<Frontend />" color="#1e293b" active={true} />
          <CodingNode position={nodePositions.backend} title="{ API_Gateway }" color="#1e293b" active={true} />
          <CodingNode position={nodePositions.database} title="[( Postgres_DB )]" color="#1e293b" />
          
          {/* AST Data Flow Lines */}
          <ConnectionLine start={nodePositions.frontend} end={nodePositions.core} />
          <ConnectionLine start={nodePositions.backend} end={nodePositions.core} />
          <ConnectionLine start={nodePositions.backend} end={nodePositions.database} />
        </>
      )}

      {/* Holographic V0-style Preview */}
      <HolographicPreview position={[-8, 4, -4]} />

      <ContactShadows position={[0, -2.9, 0]} opacity={0.4} scale={30} blur={2} far={4.5} />
      <Environment preset="city" />
    </>
  );
}

// --- Main UI Layout ---

export default function SpatialCockpit() {
  const [astData, setAstData] = useState<any>(null);

  React.useEffect(() => {
    fetch("http://localhost:8080/ast?project=default")
      .then(res => res.json())
      .then(data => {
        if (data.status === "ok") {
          setAstData(data.topology);
        }
      })
      .catch(console.error);
  }, []);

  return (
    <div className="flex h-screen w-full bg-[#030303] text-zinc-300 overflow-hidden font-sans">
      {/* Left Sidebar */}
      <nav className="w-16 border-r border-zinc-900 flex flex-col items-center py-6 gap-8 bg-[#050505]/80 backdrop-blur-xl z-20">
        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/20">
          <Layers className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1 flex flex-col gap-6">
          <button className="p-3 text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-xl" title="AST Graph">
            <Box className="w-5 h-5" />
          </button>
          <button className="p-3 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-xl transition-all" title="Swarm Agents">
            <BrainCircuit className="w-5 h-5" />
          </button>
          <button className="p-3 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-xl transition-all" title="Live Preview">
            <Eye className="w-5 h-5" />
          </button>
        </div>
        <button className="p-3 text-zinc-500 hover:text-white transition-all"><Settings className="w-5 h-5" /></button>
      </nav>

      {/* Main Area */}
      <main className="flex-1 relative flex flex-col">
        {/* Top Header */}
        <header className="h-16 border-b border-zinc-900 flex items-center justify-between px-8 bg-[#050505]/50 backdrop-blur-md z-10">
          <div className="flex items-center gap-4">
            <h1 className="text-[11px] font-bold tracking-[0.3em] text-zinc-400 uppercase">Atlas // Code_OS</h1>
            <div className="h-4 w-[1px] bg-zinc-800" />
            <div className="flex items-center gap-2 text-[10px] font-mono text-indigo-400">
              <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
              ELITE_SWARM: OPERATIONAL
            </div>
          </div>
        </header>

        {/* 3D Canvas */}
        <div className="flex-1 relative">
          <Canvas shadows dpr={[1, 2]}>
            <Suspense fallback={null}>
              <CockpitScene astData={astData} />
            </Suspense>
          </Canvas>

          {/* Holographic UI Overlay */}
          <div className="absolute top-6 left-6 pointer-events-none">
            <div className="bg-[#0a0a0a]/60 border border-zinc-800 p-4 rounded-2xl backdrop-blur-xl space-y-4 w-64 shadow-2xl">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-widest text-zinc-400 font-bold">Predictive Engine</span>
                <Cpu className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-[10px] mb-1"><span className="text-zinc-500">AST Parsing</span><span className="text-emerald-400">0.2ms</span></div>
                  <div className="w-full h-0.5 bg-zinc-800 rounded-full"><div className="h-full bg-emerald-500 w-[100%]" /></div>
                </div>
                <div>
                  <div className="flex justify-between text-[10px] mb-1"><span className="text-zinc-500">Speculative Drafts</span><span className="text-indigo-400">3 Nodes</span></div>
                  <div className="w-full h-0.5 bg-zinc-800 rounded-full"><div className="h-full bg-indigo-500 w-[60%]" /></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Swarm Orchestrator (Replacing standard chat) */}
        <div className="absolute right-6 top-24 bottom-6 w-96 bg-[#0a0a0a]/80 border border-zinc-800 rounded-2xl backdrop-blur-2xl flex flex-col overflow-hidden shadow-2xl z-10">
          <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/30">
            <div className="flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-indigo-400" />
              <span className="text-[11px] font-bold uppercase tracking-widest">Swarm Orchestrator</span>
            </div>
            <div className="text-[9px] font-mono bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">
              PARALLEL MODE
            </div>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {/* Mission Prompt */}
            <div className="bg-zinc-900/50 border border-zinc-800 p-3 rounded-xl">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold mb-2 block">Active Directive</span>
              <p className="text-xs text-zinc-300">"Build a real-time authentication layer and scaffold the user dashboard."</p>
            </div>

            {/* Agent Threads */}
            <div className="space-y-3">
              {/* Agent 1 */}
              <div className="border border-indigo-500/20 bg-indigo-500/5 p-3 rounded-xl relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500" />
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Frontend Agent</span>
                  <span className="text-[10px] font-mono text-zinc-500">Drafting</span>
                </div>
                <p className="text-[11px] font-mono text-zinc-400 mb-2">{`Editing <Frontend /> node...`}</p>
                <div className="flex gap-2">
                   <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" />
                   <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-100" />
                   <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-200" />
                </div>
              </div>

              {/* Agent 2 */}
              <div className="border border-emerald-500/20 bg-emerald-500/5 p-3 rounded-xl relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500" />
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Backend Agent</span>
                  <span className="text-[10px] font-mono text-emerald-500">Testing</span>
                </div>
                <p className="text-[11px] font-mono text-zinc-400 mb-2">{`Validating { API_Gateway } JWT tokens...`}</p>
                <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 w-[85%]" />
                </div>
              </div>
            </div>
          </div>
          
          <div className="p-4 border-t border-zinc-800 bg-zinc-900/30">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Command the swarm..." 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl py-3 pl-4 pr-12 text-xs focus:outline-none focus:border-indigo-500/50 shadow-inner"
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 text-white bg-indigo-600 hover:bg-indigo-500 p-2 rounded-lg transition-colors">
                <Play className="w-3 h-3 fill-current" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
