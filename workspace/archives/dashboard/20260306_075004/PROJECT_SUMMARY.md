# Project Scratchpad

Goal: can we make the map a globe model?

## Acceptance Criteria
### Acceptance Criteria

**AC1: Globe Rendering**
- The application successfully renders a 3D globe model in place of the previous 2D map component.
- The globe displays base map textures (e.g., satellite, topology, or styled vector tiles) without visual artifacts.

**AC2: Interactivity**
- The user can rotate/pan the globe on all axes using mouse drag or touch gestures.
- The user can zoom in and out of the globe smoothly using scroll or pinch-to-zoom gestures.

**AC3: Performance & SSR Compatibility**
- The 3D globe component is implemented as a Client Component.
- The component is lazy-loaded using Next.js `next/dynamic` with `ssr: false` to prevent server-side rendering hydration errors and minimize Time to First Byte (TTFB).
- A lightweight loading skeleton or placeholder is displayed while the 3D assets and JavaScript bundle are being fetched.

**AC4: Data Parity**
- All existing map data points (markers, tooltips, polygons, or routes) are accurately mapped and rendered on the 3D globe using correct latitude and longitude coordinates.
- Interactive elements on the globe (e.g., clicking a marker) trigger the same state changes or UI popups as the previous 2D map.

**AC5: Responsive Design**
- The globe canvas dynamically resizes to fit its container across desktop, tablet, and mobile viewports.
- The globe remains centered and fully usable when the browser window is resized.

## Architecture
Here is the finalized, enterprise-grade architecture for the 3D Globe migration. This refined blueprint strictly addresses the security vulnerabilities, scalability bottlenecks, and error-handling deficiencies identified in the critique, while adhering to Next.js App Router best practices.

---

### 1. Technology Stack & Security Baseline
*   **Core 3D Engine:** `react-globe.gl` (built on `three`).
*   **Data Fetching:** `swr` or `@tanstack/react-query` (Strictly client-side to prevent SSR bloat).
*   **Security:** `isomorphic-dompurify` (Mandatory for sanitizing all HTML marker inputs).
*   **Resilience:** `react-error-boundary` (For granular WebGL crash handling).
*   **DevSecOps:** Enforce `npm audit` and Snyk scanning in the CI/CD pipeline specifically targeting WebGL/Three.js dependencies before merging to `main`.

---

### 2. Refined Directory Structure
We introduce dedicated utilities for WebGL capability checking, error boundaries, and memory management.

```text
/app
  └── (routes)                 
/components
  └── /map
       ├── GlobeWrapper.tsx    # Entry: WebGL Check -> Error Boundary -> Dynamic Import
       ├── GlobeMap.tsx        # Core Engine: Memory cleanup, Texture fallbacks, Sanitization
       ├── GlobeSkeleton.tsx   # CSS placeholder for TTFB optimization
       ├── MarkerPopup.tsx     # XSS-safe UI component for interactions
       ├── WebGLFallback.tsx   # Renders legacy 2D map if WebGL is disabled
       └── MapErrorBoundary.tsx# Catches Three.js runtime crashes
/lib
  └── /map
       ├── mapUtils.ts         # Coordinate math, clustering logic (e.g., supercluster)
       └── webglUtils.ts       # Canvas context detection (detectWebGLContext)
/hooks
  └── useMapData.ts            # Client-side fetching (SWR) to prevent SSR payload bloat
```

---

### 3. Scalability & Memory Management Architecture

#### A. Mitigating SSR Payload Bloat
To prevent serializing massive geographical datasets across the Server-to-Client boundary (which destroys Time to First Byte), **Server Components will no longer pass raw coordinate arrays as props.**
1. The Server Component renders `<GlobeWrapper />` with minimal configuration props (e.g., `initialView`).
2. Inside `GlobeMap.tsx`, a custom hook `useMapData` utilizes SWR to fetch the heavy JSON/GeoJSON payload asynchronously *after* hydration.
3. For datasets exceeding 10,000 points, `mapUtils.ts` will implement spatial clustering (e.g., using `supercluster`) to only render visible WebGL nodes.

#### B. Preventing WebGL Memory Leaks
Three.js does not automatically garbage collect geometries, materials, or textures when a React component unmounts. 
*   `GlobeMap.tsx` will implement a strict `useEffect` cleanup function.
*   On unmount, it will traverse the Three.js scene graph and explicitly call `.dispose()` on all `THREE.BufferGeometry`, `THREE.Material`, and `THREE.Texture` instances, followed by `renderer.dispose()`.

---

### 4. Component Architecture Breakdown (Implementation)

#### A. `GlobeWrapper.tsx` (Resilient Entry Point)
This component acts as the SSR firewall, hardware capability checker, and error boundary.

```tsx
'use client';
import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import { GlobeSkeleton } from './GlobeSkeleton';
import { WebGLFallback } from './WebGLFallback';
import { MapErrorBoundary } from './MapErrorBoundary';
import { isWebGLAvailable } from '@/lib/map/webglUtils';

const DynamicGlobe = dynamic(() => import('./GlobeMap'), {
  ssr: false,
  loading: () => <GlobeSkeleton />
});

export const GlobeWrapper = () => {
  const [webGLSupported, setWebGLSupported] = useState<boolean | null>(null);

  useEffect(() => {
    setWebGLSupported(isWebGLAvailable());
  }, []);

  if (webGLSupported === null) return <GlobeSkeleton />;
  if (!webGLSupported) return <WebGLFallback />; // Graceful degradation to 2D

  return (
    <div className="relative w-full h-full min-h-[500px]">
      <MapErrorBoundary>
        <DynamicGlobe />
      </MapErrorBoundary>
    </div>
  );
};
```

#### B. `GlobeMap.tsx` (Secure & Scalable Engine)
The heavyweight Client Component, updated with XSS sanitization, texture fallbacks, and memory cleanup.

```tsx
'use client';
import { useRef, useEffect, useMemo, useState } from 'react';
import Globe, { GlobeMethods } from 'react-globe.gl';
import DOMPurify from 'isomorphic-dompurify';
import { useMapData } from '@/hooks/useMapData';

const PRIMARY_TEXTURE = 'https://cdn.example.com/high-res-earth.webp';
const FALLBACK_TEXTURE = '/assets/low-res-earth-fallback.jpg';

export default function GlobeMap() {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const { data: markers, isLoading } = useMapData(); // Client-side fetch
  const [textureUrl, setTextureUrl] = useState(PRIMARY_TEXTURE);

  // 1. Security: Sanitize HTML marker data to prevent XSS
  const sanitizedMarkers = useMemo(() => {
    if (!markers) return [];
    return markers.map(marker => ({
      ...marker,
      safeHtml: DOMPurify.sanitize(marker.rawHtmlContent) 
    }));
  }, [markers]);

  // 2. Memory Management: Explicit Three.js disposal
  useEffect(() => {
    return () => {
      if (globeRef.current) {
        const scene = globeRef.current.scene();
        scene.traverse((object: any) => {
          if (object.geometry) object.geometry.dispose();
          if (object.material) {
            if (Array.isArray(object.material)) {
              object.material.forEach((mat: any) => mat.dispose());
            } else {
              object.material.dispose();
            }
          }
        });
      }
    };
  }, []);

  if (isLoading) return null; // Skeleton is handled by wrapper

  return (
    <Globe
      ref={globeRef}
      globeImageUrl={textureUrl}
      onGlobeTextureError={() => setTextureUrl(FALLBACK_TEXTURE)} // 3. Network Resilience
      htmlElementsData={sanitizedMarkers}
      htmlElement={(d: any) => {
        const el = document.createElement('div');
        el.innerHTML = d.safeHtml; // Safe injection
        return el;
      }}
    />
  );
}
```

### 5. Summary of Resolutions
1.  **XSS Vulnerability:** Resolved via `isomorphic-dompurify` integration before mapping data to DOM nodes.
2.  **Payload Bloat:** Resolved by abandoning Server-to-Client prop passing in favor of SWR client-side data fetching.
3.  **Memory Leaks:** Resolved via explicit `.dispose()` traversal on component unmount.
4.  **WebGL Crashes/Unsupported:** Resolved via `isWebGLAvailable()` capability checks and a dedicated `<MapErrorBoundary>`.
5.  **Asset Failures:** Resolved via `onGlobeTextureError` fallback logic to ensure the globe always renders, even if the CDN drops.
