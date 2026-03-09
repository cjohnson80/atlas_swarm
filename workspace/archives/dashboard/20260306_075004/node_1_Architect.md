# Architectural Decision Record: Next.js 3D Geospatial Visualization

As the Lead Geospatial WebGL Architect, I have evaluated the landscape of 3D globe rendering engines within the context of a modern Next.js (App Router) architecture. Our primary constraints are **Time to Interactive (TTI)**, **main-thread performance** (avoiding React render cycle blocking), and **hydration stability**.

## 1. Objective Evaluation & Selection

| Library | Next.js Compatibility | Bundle Size | Marker Performance (Instancing) | Learning Curve | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CesiumJS** | ❌ Poor (Requires complex Webpack/Turbopack custom loaders for Web Workers & WASM) | ⚠️ Massive (~3MB+) | 🏆 Exceptional (True 3D Tiles / Terrain) | Steep | **Overkill.** Unjustified bundle size unless rendering photorealistic 3D cityscapes or high-precision terrain models. |
| **deck.gl** | 🟡 Fair (React wrapper is good, but `GlobeView` is less mature than standard Web Mercator) | 🟡 Medium (~500KB) | 🏆 Exceptional (Millions of points via luma.gl) | Moderate | **Strong Contender.** Best for massive data, but lacks out-of-the-box "globe aesthetic" polish (atmosphere, stars). |
| **react-globe.gl** | 🟢 Good (Requires strict `next/dynamic` SSR disable) | 🟢 Small/Medium (Relies on Three.js) | 🟢 Great (~10k-50k points via Three.js instanced meshes) | Easy | **Selected.** Provides the best balance of visual fidelity, Next.js integration, and performance for marker/arc-based visualizations. |

### **The Selection: `react-globe.gl` (with strict architectural constraints)**
While `deck.gl` wins on raw throughput, `react-globe.gl` provides the exact primitives required for a standard analytical globe dashboard with significantly less boilerplate. To overcome its Three.js main-thread limitations, we will strictly decouple data transformation from the React render loop.

---

## 2. Component Interface (TypeScript)

We must isolate the WebGL context from the rest of the React tree. The component API must be agnostic, allowing us to swap the underlying engine if requirements scale beyond Three.js limits.

```typescript
// types/geospatial.ts
export interface GeoMarker {
  id: string;
  lat: number;
  lng: number;
  size: number;
  color: string;
  metadata?: Record<string, unknown>;
}

export interface ViewportState {
  lat: number;
  lng: number;
  altitude: number;
}

// components/Globe/GlobeInterface.ts
export interface InteractiveGlobeProps {
  /** Pre-computed, flat array of markers to avoid render-time mapping */
  markers: Float32Array | GeoMarker[]; 
  /** Controlled viewport state */
  viewport?: ViewportState;
  /** Callback for WebGL-native click events */
  onMarkerClick?: (markerId: string) => void;
  /** Callback to sync WebGL camera movements back to React state */
  onViewportChange?: (viewport: ViewportState) => void;
  /** Theme configuration (static, should not trigger re-renders) */
  theme?: 'dark' | 'light' | 'satellite';
}
```

### Next.js Integration Strategy
WebGL cannot be Server-Side Rendered. The component must be dynamically imported at the page level to prevent hydration mismatches and `window is not defined` errors.

```tsx
// components/Globe/index.tsx
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/Skeleton';

export const InteractiveGlobe = dynamic(
  () => import('./GlobeRenderer').then((mod) => mod.GlobeRenderer),
  {
    ssr: false,
    loading: () => <Skeleton className="w-full h-full rounded-full" />
  }
);
```

---

## 3. Performant Data Mapping Strategy

**The Rule:** *Never iterate over large geospatial datasets inside a React component's render body.* 

1.  **Ingestion & Normalization:** Raw data (e.g., GeoJSON) must be parsed outside the main thread using a **Web Worker** or during the Next.js Server Component data fetching phase.
2.  **Flat Structures:** Transform deeply nested GeoJSON into a flat array of `GeoMarker` objects. For extreme performance (>50k markers), transform data into a `Float32Array` (Interleaved buffer: `[lat, lng, size, r, g, b, ...]`) to feed directly into WebGL attributes, bypassing JavaScript garbage collection overhead.
3.  **Memoization:** If mapping must occur on the client, wrap it in a custom hook utilizing `useMemo` with strict dependency arrays.

```typescript
// hooks/useGeospatialData.ts
import { useMemo } from 'react';

export function useOptimizedMarkers(rawData: RawAPIResponse[]) {
  return useMemo(() => {
    // This heavy loop only runs when rawData reference changes
    return rawData.map(item => ({
      id: item.uuid,
      lat: normalizeLat(item.coordinates[1]),
      lng: normalizeLng(item.coordinates[0]),
      size: Math.max(1, Math.log(item.value)),
      color: extractColor(item.category)
    }));
  }, [rawData]);
}
```

---

## 4. State Management Flow

To prevent catastrophic re-render loops, we must sever the two-way data binding between the React UI and the WebGL Canvas. We will use **Zustand** for atomic, selector-based state updates.

### Architecture Flow:
1.  **UI Interaction (e.g., clicking a sidebar list):**
    *   Sidebar calls `useGlobeStore.getState().setViewport({ lat, lng })`.
    *   The Globe component subscribes *only* to `state.viewport`. It receives the new coords and triggers a `globeRef.current.pointOfView()` transition (an imperative WebGL call, bypassing React renders).
2.  **Globe Interaction (e.g., panning the globe):**
    *   User drags the WebGL canvas.
    *   `react-globe.gl` fires `onZoom` or `onMove`.
    *   We **debounce** this event (e.g., 200ms) and call `useGlobeStore.getState().setViewport(newCoords)`.
    *   React UI components (like a coordinate display widget) subscribed to `state.viewport` update independently without forcing the Globe canvas to re-render.

```typescript
// store/globeStore.ts
import { create } from 'zustand';

interface GlobeStore {
  viewport: ViewportState;
  selectedMarkerId: string | null;
  setViewport: (vp: ViewportState) => void;
  setSelectedMarker: (id: string | null) => void;
}

export const useGlobeStore = create<GlobeStore>((set) => ({
  viewport: { lat: 0, lng: 0, altitude: 2.5 },
  selectedMarkerId: null,
  setViewport: (vp) => set({ viewport: vp }),
  setSelectedMarker: (id) => set({ selectedMarkerId: id }),
}));
```

### Summary of the Architect's Directive
By selecting `react-globe.gl`, encapsulating it within a dynamically imported boundary, flattening our data structures prior to render, and utilizing Zustand to orchestrate imperative WebGL camera movements against declarative React state, we achieve a highly performant, visually stunning Next.js geospatial application.