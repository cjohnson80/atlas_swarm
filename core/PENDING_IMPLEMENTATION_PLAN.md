# ATLAS_SYNC_01: SPATIAL_CODE_OS & PERFORMANCE_V3_STRATEGY

## 1. SECURE_FLIGHT_CONTROLLER (SFC-H) - ATOMIC CONCURRENCY
- **Sharded Registry:** Implement `_in_flight_shards = [dict() for _ in range(os.cpu_count() * 4)]` with a dedicated `threading.Lock` per shard.
- **Canonical Hashing:** Key generation via `hashlib.blake2b(json.dumps({'t': tool, 'p': payload, 'c': context_id}, sort_keys=True).encode('utf-8')).hexdigest()` to prevent delimiter injection and handle complex payloads.
- **Atomic Reaper:** Subprocess tracking via `psutil.Process(pid)`. On timeout/failure, SFC-H must issue `SIGTERM` followed by `SIGKILL` if the process persists >2s, ensuring zero-zombie state.

## 2. DYNAMIC_TIMEOUT_CALIBRATION (DTC) & RESILIENT_CIRCUIT_BREAKER
- **EMA Algorithm:** Use an Exponential Moving Average (EMA) with $\alpha=0.1$ for latency tracking. Exclude hard timeouts from the average calculation to prevent 'death spirals'; instead, increment a 'Failure_Pressure' counter.
- **Circuit Breaker (Half-Open):** 
    - `CLOSED`: Normal operation.
    - `OPEN`: Triggered when `Failure_Pressure > Threshold`. All non-critical tool calls return cached or default values.
    - `HALF-OPEN`: After a 60s cooldown, allow 5% of traffic to probe system health. If latency < P95, transition to `CLOSED`.
- **Scaling:** Hard ceilings ($T_{max}$) calculated as `min(30, P95 * 1.5)` seconds.

## 3. SPATIAL_CODE_OS: NON-EUCLIDEAN NAVIGATION
- **LOD (Level of Detail) Engine:** 
    - `LOD_0 (Macro)`: Repositories as 3D point clouds (InstancedMesh).
    - `LOD_1 (Module)`: Directories as geometric clusters; only labels and connectivity visible.
    - `LOD_2 (Atomic)`: Individual files/functions rendered as navigable nodes with syntax-highlighted textures via OffscreenCanvas.
- **Temporal Z-Axis:** Map Git history to depth. Use 'Frustum Culling' and 'Octree Partitioning' to ensure $O(1)$ rendering complexity relative to total repo size.

## 4. EXECUTION ROADMAP
- [ ] **Phase 1:** Patch `bin/atlas_core.py` with Sharded SFC-H and Canonical Hashing.
- [ ] **Phase 2:** Integrate `psutil`-based process reaping in `skills/atomic_executor.py`.
- [ ] **Phase 3:** Scaffold `frontend/src/app/cockpit/` with Three.js and the LOD Octree manager.
