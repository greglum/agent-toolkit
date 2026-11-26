---
name: half-bounce-launch
description: "Measure, audit, and optimize macOS desktop app launch time toward a half-bounce target (200 to 300 ms to interactive Frame 1) across Rust, Swift, and hybrid stacks via LaunchServices timing, Mach-O/dyld hygiene, and Frame-1 deferral. Not for UI tests (app-verifier), UI motion (ui-motion), or A/B stats (compare-experiments)."
compatibility: "Bundled Mach-O/bundle hygiene checker uses Python 3.10+ stdlib. Live binary checks use macOS Xcode CLI tools (file, lipo, otool, size, xcrun dyld_info); LaunchServices timing, external window probes, and Time Profiler traces use open, swiftc, and xcrun xctrace on macOS. Without builds or macOS tools, run the static audit and report live metrics unrun."
---

# Half-bounce launch

Measure, audit, and shrink macOS desktop application cold-launch latency toward a half-bounce Dock launch (roughly 200 to 300 ms from click to interactive Frame-1 pixels, inside Apple's 400 ms budget) while prioritizing simplicity and avoiding over-engineering.

A read-only audit edits nothing and builds nothing. Stay inside the requested repository scope and preserve its existing gates, test policy, signing rules, and unrelated edits. Never fabricate timings, keep an `LSUIElement` login-item daemon resident, show non-interactive splash screens, or swizzle private AppKit selectors to fake speed.

## 1. Gate platform and choose live vs static mode

Confirm the target platform before measuring (`SDKROOT`, `Cargo.toml`, `LC_BUILD_VERSION`). If an Xcode project builds iOS/iPadOS only (`SDKROOT = iphoneos`), declare macOS LaunchServices checks `NOT APPLICABLE` rather than `NOT RUN` and audit against Apple's iOS launch contract (`XCTApplicationLaunchMetric`, `OSSignposter`, `MXAppLaunchMetric`) using [stack playbooks](references/stack-playbooks.md#2-swift-and-xcode-appkit-swiftui).

### When a fresh signed macOS `.app` exists and builds are allowed
1. Package and sign a real `.app` bundle (`Info.plist`, `PkgInfo`, `codesign --force --deep --sign -`, `xattr -dr com.apple.quarantine`) rather than timing an unbundled executable.
2. Run `>= 5` LaunchServices launches (`open -n -W`), reporting coldest Run 1 separately from warm Runs `2..N` (`median`, `min`, `max`).
3. Measure interactive Frame 1 alongside AppKit milestones (`did_finish_launching_ms` stops the Dock bounce early before window creation, font loading, GPU setup, or WebView paint). Pair in-process `key=value` milestone logs with a pre-warmed external `CGWindowListCopyWindowInfo` (`kCGWindowLayer == 0`) probe.
4. Capture one `xcrun xctrace` Time Profiler trace (`life-cycle-period`, call tree, plus child WebContent processes for hybrid apps) and one `/usr/bin/time -l` resource pass (`page_reclaims`, `page_faults`, `max_rss_mb`, `peak_footprint_mb`).

### Read-only or stale-bundle static audit mode
When builds are disallowed or no Release `.app` exists, report live timings `NOT RUN` and run the static audit across the entry call graph:
- Check binary freshness (`--source-root`) and confirm existing `.app` bundles are not Debug stubs (`ENABLE_DEBUG_DYLIB`) or wrong-platform builds.
- Inspect release profile placement (workspace root `Cargo.toml` vs member crates, Xcode Release settings), macOS deployment floor, and embedded assets/sourcemaps (`include_str!`, `frontendDist`, `Assets.car`).
- Trace `main()`, `@main App.init()`, `.setup()`, and root view `body` / first paint for synchronous disk reads, JSON decodes/re-encodes, filesystem xattr/fsync writes, Keychain `SecItemCopyMatching` IPC, subprocess `which`/CLI probes, or eager SQLite integrity scans.

## 2. Check Mach-O, dyld, and bundle hygiene

Resolve `<skill-dir>` from this `SKILL.md` path so commands work from any repository directory:

```sh
python3 <skill-dir>/scripts/check_launch_hygiene.py <binary_or_App.app> --profile rust-native --require-zero-exports --source-root .
python3 <skill-dir>/scripts/check_launch_hygiene.py <App.app> --profile swift --source-root .
python3 <skill-dir>/scripts/check_launch_hygiene.py <App.app> --profile tauri --bench-log <bench.txt> --budget-ms 280
```

Read [strategies and traps](references/strategies-and-traps.md) before changing linker flags, `Info.plist`, or AppKit setup. Choose `--profile` to match the stack (`rust-native` defaults `max_dylibs=14, max_unwind_bytes=100000`; `swift` `64 / 250000`; `tauri` `30 / 250000`), and omit `--require-zero-exports` on Xcode targets using `TEST_HOST`/`BUNDLE_LOADER` or `AppIntents`. Exit `0` passes, `1` fails hygiene or budget, and `2` signals missing tools or invalid arguments.

## 3. Apply measured fixes in simplicity order

1. **Universal macOS bundle and linker hygiene**: Raise `MACOSX_DEPLOYMENT_TARGET` (`>= 15.0` when recent macOS/Apple Silicon fits) so `ld` emits `LC_DYLD_CHAINED_FIXUPS`, 4-byte `__TEXT,__init_offsets`, and compact `__unwind_info`. Add `-Wl,-dead_strip`, `-Wl,-dead_strip_dylibs`, and `-Wl,-no_exported_symbols` where exports are unneeded; never add `-Wl,-merge_zero_fill_sections` when `__DATA,__thread_bss` exists. Set fast-launch `Info.plist` keys (`NSHighResolutionCapable`, `NSSupportsAutomaticGraphicsSwitching`, `NSPrincipalClass`, `LSRequiresNativeExecution`, `NSQuitAlwaysKeepsWindows=false`); enable `NSSupportsSuddenTermination=true` only when the app needs no graceful shutdown/fsync cleanup (or guard critical work dynamically). Omit `LSMultipleInstancesProhibited` if `open -n` benchmarking runs concurrently.
2. **Stack-specific tuning**: Read [stack playbooks](references/stack-playbooks.md) and follow only the matching track (`Rust Native`, `Swift / Xcode`, or `Tauri / WebView + SQLite`).
3. **Future-scale levers**: Defer heavyweight changes (nightly `-Z build-std`, `MTLBinaryArchive`, Mergeable Libraries, mmap read-ahead, MetricKit) until profiled triggers in [strategies and traps](references/strategies-and-traps.md) fire.

## 4. Verify A/B deltas, report honestly, and capture lessons

Re-run repository test/lint gates, positive and negative `--budget-ms` checks, and paired A/B comparisons (`compare-experiments` skill methodology for noisy multi-run comparisons). Record machine/OS/toolchain, coldest Run 1 separately from warm Runs `2..N` medians, exact size/dylib/fixup/rusage changes, and distinct `PASS`, `FAIL`, `UNAVAILABLE`, `NOT RUN`, and `NOT APPLICABLE` statuses.

When a real-repo run exposes a new stack trap, wording conflict, or hygiene checker gap, capture portable lessons into this bundle via `learn-taste`.
