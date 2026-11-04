#!/usr/bin/env python3
"""Inventory declared GLB metadata locally; never load referenced files or validate a scene."""

import argparse
import json
from pathlib import Path
import struct


def read_document(path):
    with path.open("rb") as source:
        size = source.seek(0, 2)
        source.seek(0)
        header = source.read(12)
        if len(header) != 12:
            raise ValueError("GLB header is truncated")
        magic, version, declared_size = struct.unpack("<4sII", header)
        if magic != b"glTF" or version != 2:
            raise ValueError("Expected a GLB version 2 container")
        if declared_size != size:
            raise ValueError("GLB declared length does not match file size")
        document, chunks = None, []
        while source.tell() < size:
            header = source.read(8)
            if len(header) != 8:
                raise ValueError("GLB chunk header is truncated")
            length, kind = struct.unpack("<I4s", header)
            if length % 4 or source.tell() + length > size:
                raise ValueError("GLB chunk is unaligned or extends past the file")
            if not chunks and kind != b"JSON":
                raise ValueError("First GLB chunk must be JSON")
            if kind == b"JSON":
                if chunks:
                    raise ValueError("GLB contains an extra JSON chunk")
                document = json.loads(source.read(length).decode("utf-8"))
            else:
                if kind == b"BIN\0" and len(chunks) != 1:
                    raise ValueError("GLB BIN chunk must occur once, directly after JSON")
                source.seek(length, 1)
            chunks.append({"type_hex": kind.hex(), "bytes": length})
    if not isinstance(document, dict):
        raise ValueError("GLB JSON must contain an object")
    asset = document.get("asset")
    if not isinstance(asset, dict) or asset.get("version") != "2.0":
        raise ValueError("Expected glTF asset.version 2.0")
    return document, size, chunks


def objects(document, key):
    value = document.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be an array of objects")
    return value


def extensions(document, key):
    value = document.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be an array of strings")
    return value


def inspect(path):
    document, size, chunks = read_document(path)
    images = objects(document, "images")
    buffers = objects(document, "buffers")
    external = []
    for key, entries in (("images", images), ("buffers", buffers)):
        for index, entry in enumerate(entries):
            uri = entry.get("uri")
            if uri is not None:
                if not isinstance(uri, str):
                    raise ValueError(f"{key}[{index}].uri must be a string")
                if not uri.startswith("data:"):
                    external.append({"collection": key, "index": index})
    return {
        "status": "INSPECTED",
        "scope": "Declared metadata only; resources, geometry and rendering NOT VALIDATED",
        "bytes": size,
        "chunks": chunks,
        "extensions_used": extensions(document, "extensionsUsed"),
        "extensions_required": extensions(document, "extensionsRequired"),
        "nodes": len(objects(document, "nodes")),
        "meshes": len(objects(document, "meshes")),
        "materials": len(objects(document, "materials")),
        "images": [{"index": index, "mime_type": image.get("mimeType"),
                    "buffer_view": image.get("bufferView"), "has_uri": "uri" in image}
                   for index, image in enumerate(images)],
        "skins": objects(document, "skins"),
        "mesh_primitives": [{"mesh": index, "name": mesh.get("name"),
                           "primitives": objects(mesh, "primitives")}
                          for index, mesh in enumerate(objects(document, "meshes"))],
        "animations": objects(document, "animations"),
        "external_resources": external,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("glb", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.glb)
        rendered = json.dumps(report, indent=2, allow_nan=False)
        code = 0
    except OSError as error:
        rendered, code = json.dumps({"status": "UNAVAILABLE", "error": str(error)}, indent=2), 2
    except (ValueError, UnicodeError) as error:
        rendered, code = json.dumps({"status": "ERROR", "error": str(error)}, indent=2), 1
    print(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
