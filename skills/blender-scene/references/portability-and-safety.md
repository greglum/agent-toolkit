# Blender portability, headless execution, and MCP safety

Read this before writing `bpy` scripts across Blender versions or using a live Blender MCP
connection.

## Headless CLI execution order

Blender evaluates command-line flags strictly left to right:

```sh
blender -b --factory-startup scene.blend -P build_prop.py -- --out prop.glb
```

- `-b` (`--background`) runs without opening a window.
- `--factory-startup` skips user preferences, custom startup files, and local add-ons so the
  script produces reproducible results across machines.
- Place any `.blend` input **before** `-P`: placing `-P` first runs the script against the
  empty factory startup scene instead of the target file.
- Pass custom script arguments after `--` and parse `sys.argv[sys.argv.index("--") + 1:]`.

## Version portability (Blender 3.x, 4.x, and 5.x)

- **Localized node names:** find shader nodes by `node.type` (`BSDF_PRINCIPLED`, `TEX_IMAGE`,
  `MIX`), never by English name (`nodes["Principled BSDF"]`).
- **Principled BSDF sockets (4.0+):** look up renamed sockets with a fallback helper:
  `inputs.get("Emission Color") or inputs.get("Emission")`,
  `inputs.get("Subsurface Weight") or inputs.get("Subsurface")`,
  `inputs.get("Specular IOR Level") or inputs.get("Specular")`,
  `inputs.get("Coat Weight") or inputs.get("Coat")`,
  `inputs.get("Sheen Weight") or inputs.get("Sheen")`,
  `inputs.get("Transmission Weight") or inputs.get("Transmission")`.
- **EEVEE engine identifier:** EEVEE used `BLENDER_EEVEE_NEXT` in Blender 4.2 through 4.x and
  `BLENDER_EEVEE` before 4.2 and in 5.x. Probe the active engine or assign inside
  `try`/`except TypeError` rather than hardcoding one enum string.
- **Slotted actions (4.4+ / 5.0+):** Blender 5.0 removed `Action.fcurves`. Use
  `obj.keyframe_insert(...)` for keyframing and access fcurves via
  `bpy_extras.anim_utils.action_get_channelbag_for_slot(...)` with fallback to `action.fcurves`
  on older versions.
- **RNA introspection:** inspect `bl_rna.properties` or `get_rna_type().properties` whenever an
  enum or operator argument varies across versions.
- **Mode cleanup:** wrap any `bpy.ops.object.mode_set(...)` call in `try`/`finally` so failures
  do not leave the scene stuck in Edit or Pose mode.

## Live Blender MCP safety and telemetry boundaries

When working through an existing `mcp-for-blender` setup:

- **Arbitrary Python execution:** `execute_blender_code` executes arbitrary Python inside the
  live Blender process. Save the `.blend` file before running generated code and break complex
  edits into small verified steps.
- **Unauthenticated socket:** the addon's TCP socket has no authentication or encryption. Keep
  it bound to `localhost`; never bind `0.0.0.0` or expose it on an untrusted network. Use an
  SSH tunnel if remote access is required.
- **Telemetry default:** `mcp-for-blender` sends minimal anonymous usage events by default
  (install UUID, session ID, tool name, duration, Blender version) unless
  `DISABLE_TELEMETRY=true` is set in the MCP server environment. Full prompts, code, and
  screenshots are opt-in. Set `DISABLE_TELEMETRY=true` when telemetry is unwanted.
- **External asset licenses:** Poly Haven assets are CC0 (API terms request source disclosure),
  whereas most Poly Pizza and many Sketchfab models are CC-BY and require creator attribution.
  Preserve attribution properties on imported objects and in the project asset ledger. Hosted
  3D generation (Meshy, Tripo, Hyper3D, Hunyuan3D, World Labs) requires separate authorization
  and API/credit governance.

## Sources and recheck triggers

Original synthesis observed November 25, 2026. No upstream code or prose copied:

- `ahujasid/mcp-for-blender` at `a5a8acf2c6` (MIT, 2026-11-18): `README.md`,
  `src/blender_mcp/guides/scene.md`, `src/blender_mcp/guides/bpy.md`,
  `src/blender_mcp/telemetry.py`.
- `@flxrnc`, *The Fable 5.2 Motion Playbook* (observed 2026-11-25 via secondary extraction of
  post `2120207374250049675` / Article `2120190721084862464`, published 2026-11-10): Lesson 7
  headless `blender -b --factory-startup -P` costume workflow and clearance checks.
- Blender official CLI documentation (headless `-b`, `--factory-startup`, left-to-right option
  evaluation).

Recheck on Blender major releases (5.x/6.x) or `mcp-for-blender` protocol/telemetry changes.
