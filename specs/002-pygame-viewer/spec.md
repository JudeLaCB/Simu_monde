# Phase 1V — Minimal Pygame World Viewer

**Status:** APPROVED FOR IMPLEMENTATION  
**Risk:** STANDARD  
**Issue:** #7

## Goal

Create the first real graphical view of Simu_monde while preserving a strict boundary between simulation logic and presentation.

The result must also be distributable on Windows as a double-clickable `SimuMonde.exe` that does not require the user to open a terminal.

## Architecture invariant

```text
simu_monde.core
    owns meters, state, time, deterministic RNG
          |
          | read/use public API
          v
simu_monde.adapters.pygame_viewer
    owns pixels, camera/view transform, drawing, input
          |
          v
       Pygame
```

Forbidden dependency direction:

```text
core -> pygame
core -> pyinstaller
core -> pixels
```

The core must remain importable and testable on a machine where Pygame is not imported by core modules.

## Package layout

Preferred layout:

```text
src/simu_monde/adapters/pygame_viewer/
├── __init__.py
├── transform.py
├── renderer.py
└── app.py

scripts/
├── run_viewer.py
└── build_windows_exe.ps1

.github/workflows/
└── build-windows-exe.yml
```

A different small file split is acceptable if the same boundaries remain obvious.

## Dependencies

Add Pygame as an optional viewer dependency rather than a core runtime dependency.

Preferred extras:

```toml
[project.optional-dependencies]
viewer = [
  "pygame>=2.6,<3",
]
build = [
  "pyinstaller>=6,<7",
]
```

Existing dev dependencies remain intact.

PyInstaller is a build dependency, not a core dependency.

## World-to-screen transform

Implement a pure, unit-testable transform object or functions that do not require an open Pygame window.

Inputs:

- `WorldBounds`;
- current viewport width/height in pixels;
- optional visual margin/padding.

Requirements:

- world origin is logically bottom-left;
- +X points right;
- +Y points up;
- screen Y is inverted only in the adapter;
- resizing preserves world aspect ratio;
- if viewport aspect ratio differs from world aspect ratio, center the rendered world with letterboxing/margins rather than distorting coordinates;
- mapping must work for configurable world dimensions, not only 1000 × 1000.

Reference mapping inside the computed world viewport:

```text
screen_x = viewport_left + world_x * uniform_scale
screen_y = viewport_bottom - world_y * uniform_scale
```

where `uniform_scale` is the same on X and Y.

Do not clamp out-of-world positions silently inside the transform. Core membership and visual rendering are separate concerns.

## Viewer application

The viewer creates a normal core simulation using public core objects.

Preferred startup scenario:

```python
SimulationConfig(
    dt_seconds=0.1,
    seed=42,
)
```

Default dimensions therefore remain 1000 m × 1000 m.

Render at minimum:

- world boundary rectangle;
- several simple marker circles whose positions are represented by core `Position2D` objects;
- current tick;
- current simulation time;
- concise control help.

No ecological entity type should be invented just to draw a marker.

## Minimal controls

Required:

- close window normally;
- `Space`: run/pause;
- `Right Arrow` or another documented single key: advance exactly one tick while paused.

Viewer may start paused to make the core/viewer separation obvious.

If continuous run mode is implemented, render FPS must not become the simulation timestep.

Use an adapter-side elapsed-time accumulator or another explicit mechanism so:

```text
simulation.step()
```

still always advances exactly one fixed core tick.

Do not change `SimulationClock.dt_seconds` based on measured FPS.

## Resize behavior

- Pygame window is resizable;
- recompute only the visual transform;
- do not mutate `WorldBounds`, `SimulationConfig`, positions, RNG, or clock because of resize;
- aspect ratio of the logical world remains correct.

## Rendering

V1 uses primitive graphics only.

Suggested:

- neutral background;
- visible rectangular world border;
- simple marker circles;
- readable text.

No sprites, textures, terrain artwork, animation system or asset pipeline.

## Executable entry point

Provide a small script:

```text
scripts/run_viewer.py
```

Its only responsibility is to import and call the viewer `main()`.

It must work both:

- from a development environment;
- when frozen by PyInstaller.

Do not put simulation rules in the script.

## Windows executable

Provide:

```text
scripts/build_windows_exe.ps1
```

that produces:

```text
dist/SimuMonde.exe
```

using PyInstaller in:

- `--onefile` mode;
- `--windowed` / no-console mode;
- clean/reproducible build mode where practical;
- application name `SimuMonde`.

The executable must launch the Pygame viewer by double-click.

No installer, MSI or auto-updater is required.

## GitHub Actions Windows artifact

Add a dedicated Windows workflow using a Windows runner.

It should:

1. check out the repository;
2. set up the supported Python version;
3. install viewer + build + test dependencies;
4. run relevant tests/checks;
5. build `SimuMonde.exe`;
6. upload the executable as a workflow artifact.

This workflow is allowed to be manual (`workflow_dispatch`) and/or run on viewer-related PR changes.

The executable must be built on Windows, not cross-compiled from Linux.

## Tests

### Transform tests

Cover:

- world origin maps to bottom-left;
- top-right world corner maps to top-right of world viewport;
- center maps to center;
- non-square viewport produces correct centered letterboxing;
- non-square world remains undistorted;
- resize changes screen mapping but not world data.

### Architecture test

Add or preserve a test that verifies core modules do not import `pygame`.

A lightweight source/import boundary assertion is enough; do not build a dependency-analysis framework.

### Simulation/view integration

Verify:

- single-step advances one core tick;
- pause does not advance core state;
- resize does not advance or mutate core state;
- same core state maps consistently to the same viewer coordinates for the same viewport.

### Packaging validation

Windows workflow must successfully build the executable.

If practical in CI, perform a lightweight frozen-app smoke check that does not hang waiting for human interaction. Do not introduce brittle GUI automation merely to satisfy this point.

## Acceptance criteria

1. `pygame` is absent from `simu_monde.core`.
2. Core tests still pass.
3. Pygame viewer opens and displays the world.
4. World coordinates remain meters in the core.
5. Aspect-ratio-preserving transform is tested.
6. Tick/time display works.
7. Run/pause/single-step preserve fixed-timestep semantics.
8. Resizing only affects presentation.
9. `SimuMonde.exe` is produced on Windows.
10. Double-clicking the executable opens the viewer without a console window.
11. GitHub Actions can produce the Windows executable artifact.
12. pytest, Ruff and mypy pass.

## Non-goals

- ecological resources;
- water visualization;
- plants;
- animals;
- movement model;
- memory;
- perception;
- AI;
- sprites;
- zoom/pan;
- save/load;
- installer;
- release updater.

## STOP conditions

Stop and return to the Primary Pilot if implementation appears to require:

- changing core coordinate semantics;
- changing world bounds semantics;
- changing timestep behavior;
- storing pixel positions in the core;
- importing Pygame from core;
- creating fake entity/domain types only for rendering;
- adding ecological behavior;
- changing RNG semantics.

## Completion report

Codex should report:

1. files changed;
2. viewer architecture;
3. controls;
4. transform behavior;
5. test/check results;
6. Windows executable build evidence;
7. artifact/workflow evidence;
8. deviations, if any;
9. PR link.
