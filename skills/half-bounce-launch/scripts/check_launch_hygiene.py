#!/usr/bin/env python3
"""Inspect macOS Mach-O binaries, .app bundles, and LaunchServices budgets."""

from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import statistics
import subprocess
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from macho_inspect import (
    check_source_staleness,
    inspect_bundle_metadata,
    parse_dyld_dylibs,
    parse_dyld_export_count,
    parse_dyld_fixup_count,
    parse_otool_big_l,
    parse_otool_l,
    parse_size_m,
    version_ge,
)

SYSTEM_PREFIXES = ("/System/Library/", "/usr/lib/")
PROFILE_DEFAULTS = {
    "rust-native": {"max_dylibs": 14, "max_unwind_bytes": 100_000},
    "swift": {"max_dylibs": 64, "max_unwind_bytes": 250_000},
    "tauri": {"max_dylibs": 30, "max_unwind_bytes": 250_000},
}


def evaluate_hygiene(
    *,
    exact_bytes: int,
    file_out: str,
    lipo_out: str,
    otool_l_out: str,
    size_m_out: str,
    dylibs: list[dict[str, object]],
    fixup_count: int | None = None,
    export_count: int | None = None,
    expected_platform: str = "macos",
    min_os: str = "15.0",
    max_dylibs: int = 14,
    max_inits: int = 6,
    max_unwind_bytes: int = 100_000,
    max_fixups: int | None = None,
    require_zero_exports: bool = False,
    bundle_info: dict[str, object] | None = None,
    stale_binary: bool | None = None,
    stale_delta_s: float = 0.0,
    stale_watched_files: int | None = None,
) -> dict[str, object]:
    """Evaluate parsed Mach-O inspection outputs against launch-hygiene limits."""
    sizes = parse_size_m(size_m_out)
    chained_fixups, minos_str, platform = parse_otool_l(otool_l_out)
    minos_ok = minos_str is not None and version_ge(minos_str, min_os)
    platform_ok = True if expected_platform == "any" else (platform == expected_platform)

    arch_tokens = lipo_out.split()
    arch_ok = arch_tokens == ["arm64"] and "arm64" in file_out and "universal" not in file_out.lower()

    paths = [str(d["path"]) for d in dylibs]
    non_system = [p for p in paths if not p.startswith(SYSTEM_PREFIXES)]
    weak_system_count = sum(1 for d in dylibs if str(d["path"]).startswith(SYSTEM_PREFIXES) and bool(d.get("weak")))
    debug_dylib_stub = any(".debug.dylib" in p for p in paths)
    linked_dylib_count = len(paths)
    dylib_count_ok = linked_dylib_count <= max_dylibs
    non_system_ok = len(non_system) == 0

    unwind_bytes = sizes["__eh_frame"] + sizes["__gcc_except_tab"] + sizes["__unwind_info"]
    unwind_ok = unwind_bytes < max_unwind_bytes
    fixups_ok = (fixup_count <= max_fixups) if (max_fixups is not None and fixup_count is not None) else (max_fixups is None)

    mod_init_count = sizes["__mod_init_func"] // 8
    init_offsets_count = sizes["__init_offsets"] // 4
    total_init_count = mod_init_count + init_offsets_count
    init_ok = total_init_count <= max_inits
    objc_load_bytes = sizes["__objc_nlclslist"] + sizes["__objc_nlcatlist"]

    exports_ok = (export_count == 0) if require_zero_exports else True
    stale_ok = not bool(stale_binary) if stale_binary is not None else True

    checks = {
        "single_arch_arm64": arch_ok,
        "platform_ok": platform_ok,
        "chained_fixups": chained_fixups,
        "minos_ok": minos_ok,
        "linked_dylib_count_ok": dylib_count_ok,
        "zero_non_system_dylibs": non_system_ok,
        "static_initializers_ok": init_ok,
        "unwind_bytes_ok": unwind_ok,
        "fixups_ok": fixups_ok,
        "exports_ok": exports_ok,
        "not_debug_stub": not debug_dylib_stub,
        "fresh_binary": stale_ok,
    }
    return {
        "exact_bytes": exact_bytes,
        "arch": lipo_out.strip(),
        "file_type": file_out.strip(),
        "platform": platform,
        "expected_platform": expected_platform,
        "__TEXT_bytes": sizes["__TEXT"],
        "__text_bytes": sizes["__text"],
        "__const_bytes": sizes["__const"],
        "__cstring_bytes": sizes["__cstring"],
        "__thread_bss_bytes": sizes["__thread_bss"],
        "__objc_nlclslist_bytes": sizes["__objc_nlclslist"],
        "__objc_nlcatlist_bytes": sizes["__objc_nlcatlist"],
        "objc_load_bytes": objc_load_bytes,
        "unwind_bytes": unwind_bytes,
        "eh_frame_bytes": sizes["__eh_frame"],
        "gcc_except_tab_bytes": sizes["__gcc_except_tab"],
        "unwind_info_bytes": sizes["__unwind_info"],
        "mod_init_count": mod_init_count,
        "init_offsets_count": init_offsets_count,
        "total_init_count": total_init_count,
        "linked_dylib_count": linked_dylib_count,
        "weak_system_dylib_count": weak_system_count,
        "non_system_dylibs": non_system,
        "debug_dylib_stub": debug_dylib_stub,
        "fixup_count": fixup_count,
        "export_count": export_count,
        "require_zero_exports": require_zero_exports,
        "minos": minos_str or "missing",
        "min_os_limit": min_os,
        "max_dylibs_limit": max_dylibs,
        "max_inits_limit": max_inits,
        "max_unwind_bytes_limit": max_unwind_bytes,
        "max_fixups_limit": max_fixups,
        "chained_fixups": chained_fixups,
        "bundle_info": bundle_info,
        "stale_binary": stale_binary,
        "stale_delta_s": round(stale_delta_s, 1),
        "stale_watched_files": stale_watched_files,
        "checks": checks,
        "passed": all(checks.values()),
    }


def evaluate_bench_log(log_text: str, budget_ms: float) -> dict[str, object]:
    """Compute Run 1 and warm Runs 2..N medians from BENCH lines and verify budget."""
    if not math.isfinite(budget_ms) or budget_ms < 0:
        raise ValueError(f"--budget-ms must be finite and non-negative, got {budget_ms!r}")
    rows: list[dict[str, float]] = []
    for line in log_text.splitlines():
        if "total_click_to_frame1_ms=" not in line:
            continue
        kv: dict[str, float] = {}
        for k, v in re.findall(r"([a-z0-9_]+)=([0-9]+(?:\.[0-9]+)?)\b", line):
            kv[k] = float(v)
        if "total_click_to_frame1_ms" in kv:
            rows.append(kv)
    if not rows:
        raise ValueError("no benchmark rows containing total_click_to_frame1_ms found")

    single_run = len(rows) == 1
    warm = rows if single_run else rows[1:]
    warm_totals = [r["total_click_to_frame1_ms"] for r in warm]
    warm_median = statistics.median(warm_totals)
    ext_vals = [r["external_window_visible_ms"] for r in warm if "external_window_visible_ms" in r]
    return {
        "runs_total": len(rows),
        "single_run_only": single_run,
        "warm_runs": 0 if single_run else len(warm),
        "run1_total_click_to_frame1_ms": rows[0]["total_click_to_frame1_ms"],
        "warm_median_total_click_to_frame1_ms": warm_median,
        "warm_min_total_click_to_frame1_ms": min(warm_totals),
        "warm_max_total_click_to_frame1_ms": max(warm_totals),
        "warm_median_external_window_visible_ms": statistics.median(ext_vals) if ext_vals else None,
        "budget_ms": budget_ms,
        "budget_passed": warm_median <= budget_ms,
    }


def _run_tool(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def inspect_live_binary(args: argparse.Namespace) -> dict[str, object]:
    target = pathlib.Path(args.target)
    bundle_info = None
    if target.is_dir() and target.suffix == ".app":
        bin_path, bundle_info = inspect_bundle_metadata(target)
    else:
        bin_path = target
    if not bin_path.is_file():
        raise FileNotFoundError(f"binary not found: {bin_path}")

    exact_bytes = os.path.getsize(bin_path)
    tools: dict[str, str] = {}
    for key, cmd in (
        ("file", ["file", "-b", str(bin_path)]),
        ("lipo", ["lipo", "-archs", str(bin_path)]),
        ("otool_l", ["otool", "-l", str(bin_path)]),
        ("size_m", ["size", "-m", str(bin_path)]),
    ):
        res = _run_tool(cmd)
        if res.returncode != 0:
            raise RuntimeError(f"command failed ({' '.join(cmd)}): {res.stderr.strip()}")
        tools[key] = res.stdout

    dyld_dylibs = _run_tool(["xcrun", "dyld_info", "-linked_dylibs", str(bin_path)])
    if dyld_dylibs.returncode == 0 and dyld_dylibs.stdout.strip():
        dylibs = parse_dyld_dylibs(dyld_dylibs.stdout)
    else:
        otool_big_l = _run_tool(["otool", "-L", str(bin_path)])
        if otool_big_l.returncode != 0:
            raise RuntimeError(f"otool -L failed: {otool_big_l.stderr.strip()}")
        dylibs = parse_otool_big_l(otool_big_l.stdout)

    fixups_res = _run_tool(["xcrun", "dyld_info", "-fixups", str(bin_path)])
    fixup_count = parse_dyld_fixup_count(fixups_res.stdout) if fixups_res.returncode == 0 else None
    exports_res = _run_tool(["xcrun", "dyld_info", "-exports", str(bin_path)])
    export_count = parse_dyld_export_count(exports_res.stdout) if exports_res.returncode == 0 else None

    stale_binary, stale_delta_s, stale_watched = (None, 0.0, None)
    if args.source_root:
        stale_binary, stale_delta_s, stale_watched = check_source_staleness(bin_path, pathlib.Path(args.source_root))

    preset = PROFILE_DEFAULTS[args.profile]
    return evaluate_hygiene(
        exact_bytes=exact_bytes,
        file_out=tools["file"],
        lipo_out=tools["lipo"],
        otool_l_out=tools["otool_l"],
        size_m_out=tools["size_m"],
        dylibs=dylibs,
        fixup_count=fixup_count,
        export_count=export_count,
        expected_platform=args.platform,
        min_os=args.min_os,
        max_dylibs=args.max_dylibs if args.max_dylibs is not None else preset["max_dylibs"],
        max_inits=args.max_inits,
        max_unwind_bytes=args.max_unwind_bytes if args.max_unwind_bytes is not None else preset["max_unwind_bytes"],
        max_fixups=args.max_fixups,
        require_zero_exports=args.require_zero_exports,
        bundle_info=bundle_info,
        stale_binary=stale_binary,
        stale_delta_s=stale_delta_s,
        stale_watched_files=stale_watched,
    )


def format_report(hygiene: dict[str, object], budget: dict[str, object] | None) -> str:
    pf = lambda ok: "PASS" if ok else "FAIL"
    checks = hygiene["checks"]
    assert isinstance(checks, dict)
    if hygiene["fixup_count"] is None:
        fixup_line = "fixup_count=UNAVAILABLE" + (" (FAIL)" if hygiene["max_fixups_limit"] is not None else "")
    else:
        lim = f", limit <= {hygiene['max_fixups_limit']}" if hygiene["max_fixups_limit"] is not None else ""
        fixup_line = f"fixup_count={hygiene['fixup_count']} ({pf(checks['fixups_ok'])}{lim})"
    if hygiene["export_count"] is None:
        export_line = "export_count=UNAVAILABLE" + (" (FAIL)" if hygiene["require_zero_exports"] else "")
    else:
        status_note = f" ({pf(checks['exports_ok'])})" if hygiene["require_zero_exports"] else " (NOT CHECKED)"
        export_line = f"export_count={hygiene['export_count']}{status_note}"

    lines = [
        f"arch={hygiene['arch']} ({pf(checks['single_arch_arm64'])}: {hygiene['file_type']})",
        f"platform={hygiene['platform']} ({pf(checks['platform_ok'])}, expected={hygiene['expected_platform']})",
        f"exact_bytes={hygiene['exact_bytes']} __TEXT={hygiene['__TEXT_bytes']} __text={hygiene['__text_bytes']} __const={hygiene['__const_bytes']} __cstring={hygiene['__cstring_bytes']}",
        f"__thread_bss_bytes={hygiene['__thread_bss_bytes']} objc_load_bytes={hygiene['objc_load_bytes']}",
        f"unwind_bytes={hygiene['unwind_bytes']} ({pf(checks['unwind_bytes_ok'])}, limit < {hygiene['max_unwind_bytes_limit']})",
        f"total_init_count={hygiene['total_init_count']} (mod_init={hygiene['mod_init_count']} init_offsets={hygiene['init_offsets_count']}) ({pf(checks['static_initializers_ok'])}, limit <= {hygiene['max_inits_limit']})",
        f"linked_dylib_count={hygiene['linked_dylib_count']} weak_system={hygiene['weak_system_dylib_count']} ({pf(checks['linked_dylib_count_ok'])}, limit <= {hygiene['max_dylibs_limit']})",
        f"non_system_dylibs={len(hygiene['non_system_dylibs'])} ({pf(checks['zero_non_system_dylibs'])})",
        f"debug_dylib_stub={hygiene['debug_dylib_stub']} ({pf(checks['not_debug_stub'])})",
        fixup_line,
        export_line,
        f"minos={hygiene['minos']} ({pf(checks['minos_ok'])}, limit >= {hygiene['min_os_limit']})",
        f"chained_fixups={'present' if hygiene['chained_fixups'] else 'missing'} ({pf(checks['chained_fixups'])})",
    ]
    binfo = hygiene.get("bundle_info")
    if isinstance(binfo, dict):
        lines.append(
            f"bundle layout={binfo.get('bundle_layout')} pkginfo={binfo.get('pkginfo_present')} "
            f"LSMin={binfo.get('minimum_system_version')} principal={binfo.get('ns_principal_class')} "
            f"native={binfo.get('ls_requires_native_execution')} quit_keeps_win={binfo.get('ns_quit_always_keeps_windows')} "
            f"sudden_term={binfo.get('ns_supports_sudden_termination')} high_res={binfo.get('ns_high_resolution_capable')} "
            f"gfx_switch={binfo.get('ns_automatic_graphics_switching')} multi_inst_prohibited={binfo.get('ls_multiple_instances_prohibited')} "
            f"nib={binfo.get('main_nib_or_storyboard')} siblings={len(binfo.get('sibling_executables') or [])} "
            f"frameworks={len(binfo.get('embedded_frameworks') or [])}"
        )
    if hygiene["stale_watched_files"] is not None:
        if hygiene["stale_binary"] is None:
            lines.append("stale_binary=UNAVAILABLE (watched_files=0)")
        else:
            lines.append(f"stale_binary={hygiene['stale_binary']} ({pf(checks['fresh_binary'])}, watched_files={hygiene['stale_watched_files']}, delta_s={hygiene['stale_delta_s']})")
    lines.append(f"hygiene_status={pf(bool(hygiene['passed']))}")
    if budget is not None:
        ok = bool(budget["budget_passed"])
        ext = budget["warm_median_external_window_visible_ms"]
        ext_txt = f"{ext:.2f}" if ext is not None else "n/a"
        run_tag = "single_run_only=True" if budget["single_run_only"] else f"warm_runs={budget['warm_runs']}"
        lines.append(
            f"run1_ms={budget['run1_total_click_to_frame1_ms']:.2f} {run_tag} "
            f"warm_median_ms={budget['warm_median_total_click_to_frame1_ms']:.2f} "
            f"warm_min_ms={budget['warm_min_total_click_to_frame1_ms']:.2f} "
            f"warm_max_ms={budget['warm_max_total_click_to_frame1_ms']:.2f} "
            f"external_window_visible_ms={ext_txt}"
        )
        lines.append(f"budget_status={pf(ok)} (warm_median_ms={budget['warm_median_total_click_to_frame1_ms']:.2f}, limit <= {budget['budget_ms']:.2f})")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check Mach-O or .app bundle launch hygiene and optional budget.")
    parser.add_argument("target", help="Path to Mach-O executable or .app bundle")
    parser.add_argument("--profile", choices=sorted(PROFILE_DEFAULTS), default="rust-native", help="Stack threshold preset")
    parser.add_argument("--platform", choices=("macos", "ios", "maccatalyst", "iossimulator", "any"), default="macos", help="Expected LC_BUILD_VERSION platform")
    parser.add_argument("--min-os", default="15.0", help="Minimum deployment version (default: 15.0)")
    parser.add_argument("--max-dylibs", type=int, default=None, help="Override preset max linked dylibs")
    parser.add_argument("--max-inits", type=int, default=6, help="Maximum static initializers (default: 6)")
    parser.add_argument("--max-unwind-bytes", type=int, default=None, help="Override preset strict upper bound on unwind bytes")
    parser.add_argument("--max-fixups", type=int, default=None, help="Optional maximum dyld fixups")
    parser.add_argument("--require-zero-exports", action="store_true", help="Fail if dynamic export count != 0")
    parser.add_argument("--source-root", help="Optional repo root to detect stale binaries older than source/config edits")
    parser.add_argument("--bench-log", help="Optional benchmark log containing BENCH lines")
    parser.add_argument("--budget-ms", type=float, help="Optional warm-median total_click_to_frame1_ms limit")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if (args.budget_ms is not None) != bool(args.bench_log):
        parser.error("--bench-log and --budget-ms must be provided together")
    try:
        hygiene = inspect_live_binary(args)
        budget = evaluate_bench_log(pathlib.Path(args.bench_log).read_text(encoding="utf-8"), args.budget_ms) if args.bench_log else None
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    passed = bool(hygiene["passed"]) and (True if budget is None else bool(budget["budget_passed"]))
    if args.json:
        print(json.dumps({"hygiene": hygiene, "budget": budget, "passed": passed}, indent=2))
    else:
        print(format_report(hygiene, budget))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
