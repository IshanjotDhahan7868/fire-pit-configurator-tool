"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useMemo } from "react";
import { ConfigState } from "@/lib/store";

function FirePitMesh({ config }: { config: ConfigState }) {
  const color = useMemo(() => {
    switch (config.material) {
      case "corten": return "#a16207";
      case "concrete": return "#6b7280";
      case "stone": return "#64748b";
      default: return "#1f2937";
    }
  }, [config.material]);

  const geometry = useMemo(() => {
    if (config.shape === "round") return <cylinderGeometry args={[1.1, 1.1, 0.6, 48]} />;
    if (config.shape === "rectangular") return <boxGeometry args={[2, 0.6, 1]} />;
    return <boxGeometry args={[1.2, 0.6, 1.2]} />;
  }, [config.shape]);

  return (
    <mesh castShadow receiveShadow>
      {geometry}
      <meshStandardMaterial color={color} roughness={0.6} metalness={config.material === "steel" ? 0.8 : 0.25} />
    </mesh>
  );
}

export function ConfiguratorScene({ config }: { config: ConfigState }) {
  return (
    <div className="h-80 w-full card overflow-hidden">
      <Canvas camera={{ position: [2.5, 2, 3], fov: 50 }} shadows>
        <ambientLight intensity={0.7} />
        <directionalLight position={[4, 6, 3]} intensity={1.1} castShadow />
        <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.4, 0]}>
          <planeGeometry args={[8, 8]} />
          <meshStandardMaterial color="#e2e8f0" />
        </mesh>
        <FirePitMesh config={config} />
        <OrbitControls enablePan enableZoom enableRotate />
      </Canvas>
    </div>
  );
}
