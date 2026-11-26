"""Mach-O and macOS `.app` bundle parsers for launch-hygiene inspection."""

from __future__ import annotations

import os
import pathlib
import plistlib
import re
import xml.parsers.expat

FIXUP_LINE_RE = re.compile(r"^\s*(?:0x[0-9a-fA-F]+|\S+\s+\S+\s+0x[0-9a-fA-F]+)\s+")
EXPORT_LINE_RE = re.compile(r"^\s*0x[0-9a-fA-F]+\s+")
SECTION_HEADER_RE = re.compile(r"^-[a-z0-9_]+:$")
SLICE_HEADER_RE = re.compile(r"^.+?\s+\[[^\]]+\]:$")
OTOOL_SLICE_RE = re.compile(r"^.+?\s+\(architecture\s+\S+\):$")
MACHO_MAGICS = (b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca")
PLATFORM_NAMES = {
    "1": "macos",
    "2": "ios",
    "6": "maccatalyst",
    "7": "iossimulator",
    "MACOS": "macos",
    "IOS": "ios",
    "MACCATALYST": "maccatalyst",
    "IOSSIMULATOR": "iossimulator",
}
SKIP_DIRS = {".git", "target", "node_modules", "dist", ".build", "DerivedData", "build", ".venv"}
WATCH_DIR_NAMES = ("src", "src-tauri", "crates", "apps", "Sources", "Config", "data", ".cargo")
WATCH_FILE_NAMES = ("Cargo.toml", "Cargo.lock", "build.rs", "Package.swift", "project.yml", "tauri.conf.json", "package.json", "index.html", "Info.plist")


def parse_version_tuple(raw: str) -> tuple[int, ...]:
    parts = [int(p) for p in raw.strip().split(".") if p.isdigit()]
    if not parts:
        raise ValueError(f"invalid version string: {raw!r}")
    return tuple(parts)


def version_ge(actual: str, required: str) -> bool:
    a, b = parse_version_tuple(actual), parse_version_tuple(required)
    width = max(len(a), len(b))
    return a + (0,) * (width - len(a)) >= b + (0,) * (width - len(b))


def parse_size_m(size_out: str) -> dict[str, int]:
    """Extract segment and segment-scoped section byte sizes from `size -m` output."""
    segments: dict[str, int] = {}
    sections: dict[tuple[str, str], int] = {}
    current_seg = ""
    for line in size_out.splitlines():
        seg_m = re.match(r"^\s*Segment\s+(\S+):\s+(\d+)", line)
        if seg_m:
            current_seg = seg_m.group(1)
            segments[current_seg] = int(seg_m.group(2))
            continue
        sec_m = re.match(r"^\s*Section\s+(\S+):\s+(\d+)", line)
        if sec_m and current_seg:
            sections[(current_seg, sec_m.group(1))] = int(sec_m.group(2))
    return {
        "__TEXT": segments.get("__TEXT", 0),
        "__text": sections.get(("__TEXT", "__text"), 0),
        "__const": sections.get(("__TEXT", "__const"), 0),
        "__cstring": sections.get(("__TEXT", "__cstring"), 0),
        "__eh_frame": sections.get(("__TEXT", "__eh_frame"), 0),
        "__gcc_except_tab": sections.get(("__TEXT", "__gcc_except_tab"), 0),
        "__unwind_info": sections.get(("__TEXT", "__unwind_info"), 0),
        "__mod_init_func": sum(v for (_, sec), v in sections.items() if sec == "__mod_init_func"),
        "__init_offsets": sum(v for (_, sec), v in sections.items() if sec == "__init_offsets"),
        "__thread_bss": sum(v for (_, sec), v in sections.items() if sec == "__thread_bss"),
        "__objc_nlclslist": sum(v for (_, sec), v in sections.items() if sec == "__objc_nlclslist"),
        "__objc_nlcatlist": sum(v for (_, sec), v in sections.items() if sec == "__objc_nlcatlist"),
    }


def parse_otool_l(otool_l_out: str) -> tuple[bool, str | None, str]:
    """Return (has_chained_fixups, minos_version_or_none, platform_name)."""
    chained = "LC_DYLD_CHAINED_FIXUPS" in otool_l_out
    platform, minos = "unknown", None
    build_m = re.search(r"cmd\s+LC_BUILD_VERSION\b(.*?)(?=Load command|\Z)", otool_l_out, re.S)
    if build_m:
        block = build_m.group(1)
        p_m = re.search(r"\bplatform\s+(\S+)", block)
        if p_m:
            platform = PLATFORM_NAMES.get(p_m.group(1), p_m.group(1).lower())
        m_m = re.search(r"\bminos\s+(\d+\.\d+(?:\.\d+)?)", block)
        if m_m:
            minos = m_m.group(1)
    elif "LC_VERSION_MIN_MACOSX" in otool_l_out:
        platform = "macos"
        mm = re.search(r"cmd\s+LC_VERSION_MIN_MACOSX\b.*?\bversion\s+(\d+\.\d+(?:\.\d+)?)", otool_l_out, re.S)
        minos = mm.group(1) if mm else None
    elif "LC_VERSION_MIN_IPHONEOS" in otool_l_out:
        platform = "ios"
        im = re.search(r"cmd\s+LC_VERSION_MIN_IPHONEOS\b.*?\bversion\s+(\d+\.\d+(?:\.\d+)?)", otool_l_out, re.S)
        minos = im.group(1) if im else None
    if minos is None:
        fallback = re.search(r"\bminos\s+(\d+\.\d+(?:\.\d+)?)", otool_l_out)
        minos = fallback.group(1) if fallback else None
    return chained, minos, platform


def _first_dyld_slice(dyld_out: str, header_token: str) -> list[str]:
    lines: list[str] = []
    seen_slice = False
    for line in dyld_out.splitlines():
        stripped = line.strip()
        if SLICE_HEADER_RE.match(stripped):
            if seen_slice:
                break
            seen_slice = True
            continue
        lines.append(line)
    if not seen_slice:
        return dyld_out.splitlines()
    return lines


def parse_dyld_dylibs(dyld_out: str) -> list[dict[str, object]]:
    """Parse `-linked_dylibs` for the first slice, stopping at trailing `-rpaths:`."""
    entries: list[dict[str, object]] = []
    in_table = False
    for line in _first_dyld_slice(dyld_out, "-linked_dylibs:"):
        stripped = line.strip()
        if not in_table:
            if "attributes" in stripped and "load path" in stripped:
                in_table = True
            continue
        if not stripped:
            continue
        if SECTION_HEADER_RE.match(stripped):
            break
        match = re.search(r"((?:/|@).+)$", stripped)
        if not match:
            continue
        entries.append({"path": match.group(1).strip(), "weak": "weak" in stripped[: match.start()].lower()})
    return entries


def parse_otool_big_l(otool_big_l_out: str) -> list[dict[str, object]]:
    """Parse linked dylibs from the first slice of `otool -L`."""
    entries: list[dict[str, object]] = []
    lines = otool_big_l_out.splitlines()
    for idx, line in enumerate(lines[1:], start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if OTOOL_SLICE_RE.match(stripped) or (idx > 1 and not line.startswith(("\t", " ")) and stripped.endswith(":")):
            break
        entries.append({"path": stripped.split(" (", 1)[0].strip(), "weak": False})
    return entries


def parse_dyld_fixup_count(fixups_out: str) -> int:
    return sum(1 for ln in _first_dyld_slice(fixups_out, "-fixups:") if FIXUP_LINE_RE.match(ln))


def parse_dyld_export_count(exports_out: str) -> int:
    return sum(1 for ln in _first_dyld_slice(exports_out, "-exports:") if EXPORT_LINE_RE.match(ln))


def _is_macho_file(path: pathlib.Path) -> bool:
    try:
        if path.is_symlink() or not path.is_file():
            return False
        with path.open("rb") as fh:
            return fh.read(4) in MACHO_MAGICS
    except OSError:
        return False


def inspect_bundle_metadata(app_dir: pathlib.Path) -> tuple[pathlib.Path, dict[str, object]]:
    """Resolve executable path and fast-launch Info.plist fields from a `.app` bundle."""
    macos_plist, ios_plist = app_dir / "Contents/Info.plist", app_dir / "Info.plist"
    if macos_plist.is_file():
        layout, plist_path = "macos", macos_plist
        exec_dir, fw_dir = app_dir / "Contents/MacOS", app_dir / "Contents/Frameworks"
    elif ios_plist.is_file():
        layout, plist_path = "ios", ios_plist
        exec_dir, fw_dir = app_dir, app_dir / "Frameworks"
    else:
        raise FileNotFoundError(f"Info.plist not found inside bundle: {app_dir}")

    try:
        with plist_path.open("rb") as fh:
            pl = plistlib.load(fh)
    except (plistlib.InvalidFileException, xml.parsers.expat.ExpatError, OSError, ValueError) as exc:
        raise ValueError(f"invalid Info.plist in {plist_path}: {exc}") from exc
    if not isinstance(pl, dict):
        raise ValueError(f"Info.plist root must be a dict in {plist_path}")

    exe_name = pl.get("CFBundleExecutable")
    if not isinstance(exe_name, str) or not exe_name or "/" in exe_name:
        raise ValueError(f"CFBundleExecutable missing or invalid in {plist_path}")
    exe_path = exec_dir / exe_name

    siblings = sorted(p.name for p in exec_dir.iterdir() if p.name != exe_name and _is_macho_file(p)) if exec_dir.is_dir() else []
    embedded_fw = sorted(p.name for p in fw_dir.iterdir() if not p.is_symlink()) if fw_dir.is_dir() else []
    info = {
        "bundle_layout": layout,
        "executable": str(exe_path),
        "pkginfo_present": (app_dir / "Contents/PkgInfo").is_file() if layout == "macos" else None,
        "minimum_system_version": pl.get("LSMinimumSystemVersion"),
        "ns_principal_class": pl.get("NSPrincipalClass"),
        "ls_requires_native_execution": pl.get("LSRequiresNativeExecution"),
        "ns_quit_always_keeps_windows": pl.get("NSQuitAlwaysKeepsWindows"),
        "ns_supports_sudden_termination": pl.get("NSSupportsSuddenTermination"),
        "ns_high_resolution_capable": pl.get("NSHighResolutionCapable"),
        "ns_automatic_graphics_switching": pl.get("NSSupportsAutomaticGraphicsSwitching"),
        "ls_multiple_instances_prohibited": pl.get("LSMultipleInstancesProhibited"),
        "main_nib_or_storyboard": pl.get("NSMainNibFile") or pl.get("NSMainStoryboardFile"),
        "sibling_executables": siblings,
        "embedded_frameworks": embedded_fw,
    }
    return exe_path, info


def _collect_watched_sources(source_root: pathlib.Path) -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for entry in source_root.iterdir():
        if entry.is_symlink():
            continue
        name = entry.name
        if entry.is_file() and (name in WATCH_FILE_NAMES or name.startswith("vite.config.") or name.endswith((".xcconfig", ".swift"))):
            found.append(entry)
        elif entry.is_dir():
            if name in SKIP_DIRS or name.endswith(".app"):
                continue
            if name.endswith((".xcodeproj", ".xcworkspace")):
                pbx = entry / "project.pbxproj"
                if pbx.is_file() and not pbx.is_symlink():
                    found.append(pbx)
                continue
            is_swift_dir = any(p.suffix == ".swift" for p in entry.iterdir() if p.is_file() and not p.is_symlink())
            if name in WATCH_DIR_NAMES or is_swift_dir:
                for root_dir, dirs, files in os.walk(entry, followlinks=False):
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".app")]
                    for fname in files:
                        fpath = pathlib.Path(root_dir) / fname
                        if not fpath.is_symlink():
                            found.append(fpath)
    return found


def check_source_staleness(bin_path: pathlib.Path, source_root: pathlib.Path) -> tuple[bool | None, float, int]:
    """Compare binary mtime against source/config files; returns (stale_or_none, delta_s, watched_count)."""
    if not source_root.is_dir():
        raise FileNotFoundError(f"source root not found: {source_root}")
    bin_mtime = bin_path.stat().st_mtime
    watched = _collect_watched_sources(source_root)
    if not watched:
        return None, 0.0, 0
    newest_mtime = 0.0
    for fpath in watched:
        try:
            newest_mtime = max(newest_mtime, fpath.stat().st_mtime)
        except OSError:
            continue
    if newest_mtime == 0.0:
        return None, 0.0, 0
    return newest_mtime > bin_mtime, max(0.0, newest_mtime - bin_mtime), len(watched)
