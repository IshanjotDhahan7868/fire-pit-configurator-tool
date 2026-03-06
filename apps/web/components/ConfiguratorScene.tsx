"use client";

import { Environment, OrbitControls } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import { Mesh } from "three";
import { ConfigState } from "@/lib/store";

function Flame({ sizeFactor }: { sizeFactor: number }) {
  const ref = useRef<Mesh>(null);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    ref.current.scale.y = 1 + Math.sin(clock.elapsedTime * 8) * 0.12;
    ref.current.position.y = 0.22 + Math.sin(clock.elapsedTime * 10) * 0.02;
  });
  return (
    <mesh ref={ref} position={[0, 0.22, 0]}>
      <coneGeometry args={[0.18 * sizeFactor, 0.35 * sizeFactor, 18]} />
      <meshStandardMaterial color="#fb923c" emissive="#f97316" emissiveIntensity={1.2} transparent opacity={0.95} />
    </mesh>
  );
}

function FirePitMesh({ config }: { config: ConfigState }) {
  const color = useMemo(() => {
    switch (config.material) {
      case "corten": return "#92400e";
      case "concrete": return "#6b7280";
      case "stone": return "#475569";
      default: return "#1f2937";
    }
  }, [config.material]);

  const sizeFactor = useMemo(() => ({ small: 0.8, medium: 1, large: 1.25, xl: 1.5 }[config.size_preset] ?? 1), [config.size_preset]);

  const geometry = useMemo(() => {
    if (config.shape === "round") return <cylinderGeometry args={[1.1 * sizeFactor, 1.1 * sizeFactor, 0.6, 64]} />;
    if (config.shape === "rectangular") return <boxGeometry args={[2.2 * sizeFactor, 0.6, 1.1 * sizeFactor]} />;
    return <boxGeometry args={[1.2 * sizeFactor, 0.6, 1.2 * sizeFactor]} />;
  }, [config.shape, sizeFactor]);

  return (
    <group>
      <mesh castShadow receiveShadow>
        {geometry}
        <meshStandardMaterial color={color} roughness={0.52} metalness={config.material === "steel" ? 0.85 : 0.15} />
      </mesh>
      <mesh position={[0, 0.18, 0]} castShadow>
        <cylinderGeometry args={[0.36 * sizeFactor, 0.36 * sizeFactor, 0.08, 32]} />
        <meshStandardMaterial emissive="#f97316" emissiveIntensity={0.8} color="#fdba74" />
      </mesh>
      <Flame sizeFactor={sizeFactor} />
    </group>
  );
}

export function ConfiguratorScene({ config }: { config: ConfigState }) {
  return (
    <div className="h-[340px] sm:h-[420px] w-full card overflow-hidden bg-gradient-to-b from-slate-100 to-slate-200">
      <Canvas camera={{ position: [2.8, 2.2, 3.2], fov: 46 }} shadows>
        <ambientLight intensity={0.55} />
        <directionalLight position={[5, 7, 3]} intensity={1.2} castShadow />
        <spotLight position={[-4, 6, 2]} angle={0.35} intensity={0.6} />
        <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.4, 0]}>
          <planeGeometry args={[14, 14]} />
          <meshStandardMaterial color="#dbe3ee" />
        </mesh>
        <FirePitMesh config={config} />
        <Environment preset="sunset" />
        <OrbitControls enablePan enableZoom enableRotate maxPolarAngle={Math.PI / 2.05} />
      </Canvas>
    </div>
  );
}
