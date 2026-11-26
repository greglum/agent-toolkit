# Launch optimization strategies and traps

Observed: 2026-11-22 on Apple Silicon / macOS 26 (Xcode `ld-1267` / Xcode 26, `xcrun xctrace` / `dyld_info`, `rustc 1.95` / LLVM 22, Swift 6.3). Recheck macOS SoftLinking behavior, `dyld_info` output format, Xcode debug-dylib stubs, and GPUI `CAMetalDisplayLink` support when upgrading macOS or toolchain releases.

## 1. Hygiene presets and measurement traps

| Profile preset | `max_dylibs` | `max_unwind_bytes` | Export & dylib notes |
| --- | ---: | ---: | --- |
| `rust-native` | `14` | `100,000` | Fits statically linked Rust GPU/AppKit apps (`panic = "abort"`) with `-Wl,-dead_strip_dylibs` and `-Wl,-no_exported_symbols` |
| `swift` | `64` | `250,000` | System `/usr/lib/swift/libswift*.dylib` weak overlays typically put SwiftUI/AppKit apps around 35 to 55 system dylibs; omit `--require-zero-exports` with `TEST_HOST`/`AppIntents` |
| `tauri` | `30` | `250,000` | `WKWebView` + system frameworks typically put Tauri apps around 16 to 24 shared-cache frameworks; check embedded `frontendDist` bloat in `__TEXT,__const` |

- **LaunchServices vs direct exec**: Executing `Contents/MacOS/<bin>` skips `launchd`/LaunchServices bundle lookup, `Info.plist` checks, Dock registration, and `codesign` overhead. Always benchmark `open -n -W` on a signed `.app` bundle.
- **Benchmark log schema (`--bench-log`)**: `check_launch_hygiene.py` accepts lines containing `total_click_to_frame1_ms=<ms>` and optional `external_window_visible_ms=<ms>` (excluding row 1 when `>= 2` runs exist so coldest Run 1 never skews warm medians). Emit consistent `key=value` timestamps at app startup (`main`, `did_finish_launching`, `open_window`, `frame1_request`, `frame1_presented`) and bridge WebView `requestAnimationFrame` in hybrid apps.
- **Harness skew**: Forking a fresh `python3` or Swift probe per run adds 15 to 25 ms, and first-exec AMFI validation on a newly compiled `swiftc` probe adds 150 to 200 ms to Run 1. Compile the external `CGWindowListCopyWindowInfo` probe once, run a 1 ms warmup call, and capture `t0_epoch_ms` in the same Python process right before `Popen([probe])` + `open -n -W`. Filter `kCGWindowLayer == 0` and exclude pre-existing window IDs.
- **Shared-host CPU load checks**: Prefer `sysctl -n vm.loadavg` (relative to logical cores from `sysctl -n hw.ncpu`) over `/usr/bin/uptime`, which can fail or return empty stdout in restricted agent shells. When 1-minute load is elevated from concurrent builds, mark LaunchServices wall-clock timings `UNAVAILABLE (high load)` instead of keeping skewed runs, while still checking deterministic Mach-O hygiene (`check_launch_hygiene.py`), release size, and `/usr/bin/time -l` memory/page counters (`page_reclaims`, `page_faults`, `max_rss_mb`, `peak_footprint_mb`).
- **PGO `.profraw` flush traps**: On macOS, `$TMPDIR` ends with `/`, which produces `//` inside `LLVM_PROFILE_FILE` unless trailing slashes are stripped first. Set `NSSupportsSuddenTermination = false` on instrumented `Train.app` bundles so normal exit invokes `atexit` and writes `.profraw`.

## 2. Mach-O, linker, and PGO traps

- **Xcode 26 `dyld_info -linked_dylibs` `-rpaths:` trap**: `xcrun dyld_info -linked_dylibs` appends a `-rpaths:` section after the linked-dylib table. Stop parsing when hitting another `-section:` header so `@executable_path` / `-rpaths:` lines are not miscounted as non-system dylibs.
- **Xcode `ENABLE_DEBUG_DYLIB` stubs & wrong-platform binaries**: Debug builds can link `@rpath/<Name>.debug.dylib` from a ~40 KB stub launcher exporting `___debug_blank_executor_main`. Always verify `platform` inside `LC_BUILD_VERSION` (`1=macos`, `2=ios`, `6=maccatalyst`, `7=iossimulator`, or `LC_VERSION_MIN_MACOSX` fallback) and confirm the target binary is a fresh Release build.
- **Do not pass `-Wl,-merge_zero_fill_sections` with TLS (`__thread_bss`)**: Merging `__DATA,__thread_bss` into `__DATA,__zerofill` caused `dyld` to abort before `main` (`malformed thread-local, offset=0x13B8 is larger than total size=0x20`). Keep `-Wl,-dead_strip`, `-Wl,-dead_strip_dylibs`, and `-Wl,-no_exported_symbols` where supported.
- **`__mod_init_func` vs `__init_offsets` and `+load`**: Targeting macOS 15.0+ emits 4-byte `__TEXT,__init_offsets` entries instead of 8-byte `__mod_init_func` pointers; count `(__mod_init_func // 8) + (__init_offsets // 4)`. In Swift/Obj-C apps, also watch `__DATA,__objc_nlclslist` and `__objc_nlcatlist` (`objc_load_bytes`) for non-lazy `+load` methods.
- **Order-file symbol mangling drift**: Legacy Rust `17h...E` hash stripping merges distinct generic monomorphizations (`drop_in_place`, closures) and bloats `startup.order`. Compile both PGO stages with `-C symbol-mangling-version=v0`, normalize `Cs[0-9A-Za-z]+_` against Stage 2 `-Wl,-map`, and skip unmatched fallback buckets with more than 4 candidates.
- **Keep compact unwind tables**: `-C force-unwind-tables=no` saves only ~50 KB when `minos >= 15.0` while degrading `xctrace` stack sampling and AppKit/Obj-C unwinding. Keep unwind tables enabled unless binary size is critical.
- **Empirical `opt-level` selection (`3` vs `s` vs `z`)**: On small-to-medium Rust GPU apps, `--pgo --opt-level z` shrunk `__text` by ~38% and saved ~12.5 ms in `pre_main_plus_ls_ms`, beating `opt-level=3` on both coldest Run 1 and warm median because `-C profile-use` kept hot startup paths fast. Re-benchmark `3`, `s`, and `z` as the startup critical path grows.

## 3. AppKit, `Info.plist`, and macOS runtime traps

- **`WritingToolsUILibraryCore` soft-link in `finishLaunching`**: Traces on macOS 15.2+ show `-[NSApplication _customizeMainMenu]` -> `+[NSTextView _supportsWritingTools]` calling `_sl_dlopen` for `WritingToolsUI`. Apple provides no public `Info.plist` opt-out; do not swizzle private AppKit selectors.
- **`NSSupportsSuddenTermination` safety caveat**: Setting `true` lets macOS `SIGKILL` cleanly without running teardown hooks. Keep `false` (or disable dynamically during critical sections) in apps managing child processes, session detach fences, or atomic journal `fsync` writes.
- **`Info.plist` keys**: Safe defaults are `NSHighResolutionCapable`, `NSSupportsAutomaticGraphicsSwitching`, `NSPrincipalClass = NSApplication`, `LSRequiresNativeExecution = true`, and `NSQuitAlwaysKeepsWindows = false`. Avoid `CFBundleLocalizations` unless traces show `.lproj` traversal, and omit `LSMultipleInstancesProhibited` when running `open -n` benchmarks.
- **`NSWindowAnimationBehaviorNone` and Keychain XPC**: Native Obj-C/Swift apps owning `NSWindow` can set `animationBehavior = .none` to skip `_NSWindowTransformAnimation` + `_NSDisplayLink` + SkyLight VRR IPC. Keep synchronous Keychain `SecItemCopyMatching` (`Security.framework`) lookups off `@MainActor`/main-thread launch paths because XPC to `securityd` stalls Frame 1.

## 4. Future-scale levers and cross-OS rules

| Trigger / App Profile | Lever | Action Threshold / Rationale |
| --- | --- | --- |
| Nightly toolchain allowed, size critical | `-C panic=immediate-abort` + `-Z build-std=std,panic_abort` | Eliminates `libstd` panic formatting and unwind glue (~100 to 300 KB) |
| Frame-1 malloc churn dominates trace | Evaluate `mimalloc` vs macOS 15+ `xzone` | `xzone` lives in the dyld shared cache at zero binary cost; switch only on trace proof |
| CoreText / fonts `> 25 ms` | `.AppleSystemUIFont` or subset `MemorySource` | Reduce distinct startup font families or ship exact weight slices |
| Startup JSON/TOML or embedded SQLite | `const` slices, `include_bytes!`, `rkyv`, `zerocopy`; `libsqlite3.dylib` | Avoid eager `serde_json`/double-DOM decoding on boot; compare `rusqlite` `bundled` (~1.5 MB `__TEXT`) vs system `/usr/lib/libsqlite3.dylib` when FTS5 parity permits |
| Large read-only mmap'd asset pack | `fcntl(F_RDADVISE)` or `madvise(MADV_WILLNEED)` | Sequential kernel read-ahead prevents random Frame-1 page-fault stalls |
| Rich icons / Asset catalogs | Compiled `Assets.car` (`actool`), static `.icns` | Keep runtime icon generation off startup (see Ghostty `#8734`) |
| Metal PSO cold stall `> 100 ms` | `MTLLibraryOptimizationLevelSize` (`-Os`), `MTLBinaryArchive`, lazy PSOs | Shrinks Metal IR, ships pre-compiled PSOs, and defers offscreen pipelines |
| Production telemetry & prewarm | `os_signpost` + MetricKit (`TimeToFirstDrawMetric`), `ActivePrewarm` purity | Keep `main()` pre-`didFinishLaunching` pure; never use `NSMainNibFile` or `NSUserDefaults.synchronize()` |
| Public macOS distribution | Developer ID signing, notarization, `xcrun stapler staple` | Lets Gatekeeper verify offline on first user launch |
| Windows parity | `windows_subsystem = "windows"`, Authenticode, `/DELAYLOAD`, `ID3D12PipelineLibrary`, `/ORDER` | Prevents console flash, Defender stalls, DirectWrite scans, and cold DX12 PSO hangs |
| Linux parity | `lld --symbol-ordering-file` (`llvm-bolt`), minimal `fontconfig`, `VK_PIPELINE_CACHE`, `.desktop` `StartupNotify=true`, dynamic glibc | Ensures GPU/display `dlopen` compatibility (avoid static musl for desktop GUIs) and clears busy cursors |

## 5. Cross-framework ceiling expectations

- **Swift / AppKit (native)**: ~120 to 220 ms warm ceiling with Mergeable Libraries and zero Storyboard overhead.
- **Rust + native GPU (`GPUI` / Metal)**: ~190 to 260 ms warm ceiling after PGO + `-order_file` + dylib/PSO hygiene (AppKit still dominates ~50%+ of samples).
- **Rust + `wgpu` (`egui` / `iced`)**: ~210 to 320 ms ceiling bounded by `wgpu` adapter/surface setup and shader compilation.
- **Tauri (`WKWebView`)**: ~300 to 550 ms ceiling bounded by `com.apple.WebKit.WebContent` spawn and JS parse/hydration.
- **Electron**: ~700 to 1,500+ ms; rarely meets a half-bounce budget.

## 6. Verified external references

- Halfbounce Club (interactive-pixel target): `https://halfbounce.club`
- Bounce Lab (LaunchServices cold/warm methodology): `https://bounce-lab.miho.dev`
- Apple: Improving Your App's Performance: `https://developer.apple.com/documentation/xcode/improving-your-app-s-performance`
- Apple: Configuring Your Project to Use Mergeable Libraries: `https://developer.apple.com/documentation/xcode/configuring-your-project-to-use-mergeable-libraries`
- Apple: `MTLBinaryArchive`: `https://developer.apple.com/documentation/metal/mtlbinaryarchive`
- Apple: MetricKit `MXAppLaunchMetric`: `https://developer.apple.com/documentation/metrickit/mxapplaunchmetric`
- LLVM `llvm-profdata order`: `https://llvm.org/docs/CommandGuide/llvm-profdata.html#profdata-order`
- Rust `v0` Symbol Mangling: `https://doc.rust-lang.org/rustc/symbol-mangling`
- Cargo Unstable `-Z build-std`: `https://doc.rust-lang.org/cargo/reference/unstable.html#build-std`
- Min-Sized-Rust: `https://github.com/johnthagen/min-sized-rust`
- Emerge Tools: How iOS 15 Makes Your App Launch Faster (`LC_DYLD_CHAINED_FIXUPS`): `https://www.emergetools.com/blog/posts/iOS15LaunchTime`
- Zed / GPUI: `https://github.com/zed-industries/zed`
- Ghostty Issue `#8734`: `https://github.com/ghostty-org/ghostty/issues/8734`
