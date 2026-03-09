# Project Scratchpad

Goal: What is the plan for a refactor of project GoldenEye?

## Acceptance Criteria
# Acceptance Criteria: Project GoldenEye Refactor

## 1. Architectural Mapping & Discovery
- [ ] **AC 1.1:** The existing directory structure and dependency graph in `workspace/goldeneye` are fully mapped using surgical file operations (`list_directory`, `search_files`) prior to any code modification.
- [ ] **AC 1.2:** Existing architectural blueprints (e.g., `SYNTHESIZED_ARCHITECTURE.md`, `ARCHITECTURE.md`) are reviewed, and a strict target state hierarchy (`/app`, `/components`, `/lib`, `/types`) is enforced.

## 2. Type Safety & Linting Enforcement
- [ ] **AC 2.1:** All TypeScript files are updated to strict typing standards. Zero instances of implicit or explicit `any` types remain in the refactored modules.
- [ ] **AC 2.2:** The project successfully passes all checks executed by `workspace/goldeneye/fix_types.py` and `workspace/goldeneye/fix_lint.py` without warnings or errors.

## 3. Server Component (RSC) Optimization
- [ ] **AC 3.1:** UI components are audited and maximally shifted to React Server Components (RSC) to minimize client-side JavaScript execution overhead.
- [ ] **AC 3.2:** The `"use client"` directive is strictly isolated to the leaf nodes of the component tree that require state (`useState`), lifecycle hooks (`useEffect`), or browser APIs.

## 4. Code De-duplication & Modular Assembly
- [ ] **AC 4.1:** Redundant code blocks, overlapping utility functions, and legacy research artifacts are pruned or consolidated into centralized files within `src/lib/` or `src/hooks/`.
- [ ] **AC 4.2:** Standardized UI elements are cross-referenced with the NextStep Vault (`library/components`) and replaced with verified modular components where applicable to reduce the overall codebase footprint.

## 5. Performance & Data Fetching Optimization
- [ ] **AC 5.1:** All server-side data fetching utilizes Next.js native `fetch` with appropriate caching strategies (`force-cache` or time-based `revalidate` tags) to minimize Time to First Byte (TTFB).
- [ ] **AC 5.2:** Client-side fetching (if strictly necessary) is deferred or managed via optimized caching libraries, ensuring aggressive HTTP caching headers are respected.

## 6. Verification & Build Integrity
- [ ] **AC 6.1:** The Next.js application successfully compiles via `npm run build` with zero build-breaking errors or type-check failures.
- [ ] **AC 6.2:** A final automated test confirms the application routes resolve with a `200 OK` status and no runtime console errors upon executing `npm run dev`.

## Architecture
API Error 429: {
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_requests_per_model_per_day, limit: 250, model: gemini-3.1-pro\nPlease retry in 19h33m43.700249621s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Gemini API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_requests_per_model_per_day",
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-3.1-pro"
            },
            "quotaValue": "250"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "70423s"
      }
    ]
  }
}

