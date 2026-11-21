---
name: write-swift
description: >-
  Write or revise Swift code using the target toolchain, platform, and language mode. Use
  for Swift implementation, actor isolation, async task ownership, cancellation, and error
  handling. Not for read-only implicit state-machine or statechart audits (use
  state-machine-audit), language migrations, or visual UI design.
compatibility: Requires the project's Swift toolchain and build environment for compilation. Package checks can run without Apple UI tools; platform builds and device behavior require their own SDK and runner. Without them, report source-only findings and unrun checks.
---

# Write Swift

Deliver the requested Swift change with its existing owner and build contract. A greenfield
choice starts with a concrete type and the least shared mutable state needed. An existing
project's architecture and compatibility constraints decide whether that choice fits.
For read-only audits of implicit state machines or statechart mapping without editing Swift
code, use `state-machine-audit`.

## Bind the target

Read repository instructions, the owning target, callers and closest tests. Preserve
unrelated dirty edits. Editing Swift code does not authorize commits, pushes, merges, or
toolchain and package installs.

Record the compiler from `swift --version`, language mode, deployment targets, package tools
version, SDK and enabled concurrency/isolation settings. Discover settings in the package
manifest or project and its existing build commands. If `swift` is missing, `swift --version`
fails, or the target manifest or project is unreadable or malformed, fall back to source-only
inspection (or stop and report if the target source itself cannot be read) and report
compilation and tests as `UNAVAILABLE`. A newer compiler does not imply a newer language
mode, SDK or minimum operating system. Do not enable language features or rewrite build
settings merely to match a tutorial.

Find the existing model, persistence, networking and UI state owners before adding types.
Prefer value types for independently copied data; use reference identity where the domain
requires sharing or resource lifetime. If copies must be independent, inspect nested fields:
copying a struct also copies any references it holds, so the copies can share a mutable object.
Use value storage or immutable backing by default. If copy-on-write is warranted, keep its
backing private and detach it before mutation; a computed setter that forwards to the shared
object still mutates both copies. Keep public API and stored-data compatibility within the
requested scope. Do not introduce a protocol or type erasure for one concrete use.

Done when the affected target, supported environment and responsible owner are explicit.

## Implement at the owner

Keep recoverable failures visible to the caller. Use the project's error and optional-value
contracts rather than turning failure into an empty success, forced unwrap or `try?` without
a stated policy. Preserve cleanup on both success and failure.

For asynchronous work or isolation diagnostics, read [concurrency](references/concurrency.md)
before changing task boundaries or annotations. Fix the actual state-transfer boundary;
a clean build obtained by suppressing checking is not evidence that sharing is safe.

When adapting APIs, check documentation against the discovered compiler, SDK and deployment
range. Keep a supported fallback where the project requires one. A language migration or
framework replacement is separate work unless it is part of the request.

## Verify the change

Use the project's build and test commands for the actual target. Extend the closest test
only for a material uncovered failure under the user's test policy. Retain XCTest or Swift
Testing according to that target; changing the test framework is not required to edit Swift.
If a Swift edit fails compilation, isolation checking, or existing tests, stop dependent
edits, isolate or revert the broken change if it cannot be fixed within authorized scope,
and report the partial failure with failing diagnostics.

For concurrent changes, exercise relevant cancellation, error propagation and stale-result
paths. Use explicit synchronization or controlled dependencies for ordering; a sleep does
not establish which task reached the boundary. A compiler check proves only what that
compiler and configuration checked. UI layout, accessibility, gestures, release performance
and device behavior need their own applicable running-app checks.

Finish when the requested behavior and required gates pass, or state the blocker. Report the
toolchain/target, changed owner, exact build and test commands with exit codes, and separate
passed, failed, unavailable, and unrun checks. Do not claim native selection or general skill
benefit from a successful build.

## Sources

See [source boundaries](references/concurrency.md#sources-and-limits). This bundle is original
procedure, with no upstream code, prompts or version tables copied.

The copy boundary follows the [November 13 Swift revision](https://github.com/emilkowalski/skills/blob/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/skills/write-swift/SKILL.md)
(MIT, copyright 2026 Emil Kowalski) and [Swift's value and reference guide](https://www.swift.org/documentation/articles/value-and-reference-types.html),
checked November 13, 2026. Recheck when backing storage or ownership changes.
