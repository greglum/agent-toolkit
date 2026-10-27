#!/usr/bin/env python3
"""Read local SARIF 2.1.0 into an evidence ledger, without running a scanner."""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

LEVELS = {"none", "note", "warning", "error"}
KINDS = {"notApplicable", "pass", "fail", "review", "open", "informational"}
BASELINES = {"new", "unchanged", "updated", "absent"}
MAX_BYTES = 20 * 1024 * 1024


class InvalidSarif(ValueError):
    """The supplied data violates this reader's input contract."""


def obj(value, at):
    if not isinstance(value, dict):
        raise InvalidSarif(f"{at}: expected object")
    return value


def array(value, at):
    if not isinstance(value, list):
        raise InvalidSarif(f"{at}: expected array")
    return value


def string(value, at):
    if not isinstance(value, str) or not value:
        raise InvalidSarif(f"{at}: expected nonempty string")
    return value


def index(value, items, at):
    if type(value) is not int or not 0 <= value < len(items):
        raise InvalidSarif(f"{at}: index outside available array")
    return items[value]


def enum(value, values, at):
    if not isinstance(value, str) or value not in values:
        raise InvalidSarif(f"{at}: unsupported value")
    return value


def id_matches(descriptor_id, result_id):
    if not isinstance(descriptor_id, str) or not isinstance(result_id, str):
        return False
    if result_id == descriptor_id:
        return True
    prefix = descriptor_id + "/"
    suffix = result_id[len(prefix):] if result_id.startswith(prefix) else ""
    return bool(suffix) and "/" not in suffix


def referenced(items, ref, at):
    """Indexes/GUIDs select metadata; optional IDs and names constrain that selection."""
    selected = None
    if "index" in ref:
        selected = index(ref["index"], items, at + ".index")
    if "guid" in ref:
        wanted = string(ref["guid"], at + ".guid")
        if selected is not None:
            if selected.get("guid") != wanted:
                raise InvalidSarif(f"{at}: conflicting index and GUID")
        else:
            matches = [item for item in items if item.get("guid") == wanted]
            if len(matches) != 1:
                raise InvalidSarif(f"{at}.guid: reference is missing or ambiguous")
            selected = matches[0]
    if selected is None and "id" in ref:
        wanted = string(ref["id"], at + ".id")
        matches = [item for item in items if id_matches(item.get("id"), wanted)]
        if len(matches) != 1:
            raise InvalidSarif(f"{at}.id: metadata lookup is missing or ambiguous")
        selected = matches[0]
    if selected is None:
        raise InvalidSarif(f"{at}: no metadata selector")
    if "id" in ref and not id_matches(selected.get("id"), string(ref["id"], at + ".id")):
        raise InvalidSarif(f"{at}: supplied ID does not match selected metadata")
    if "name" in ref and selected.get("name") != string(ref["name"], at + ".name"):
        raise InvalidSarif(f"{at}: supplied name does not match selected metadata")
    return selected


def rule_for(result, tool, at):
    ref = dict(obj(result.get("rule", {}), at + ".rule"))
    for outer, inner in (("ruleId", "id"), ("ruleIndex", "index")):
        if outer in result:
            if inner in ref and ref[inner] != result[outer]:
                raise InvalidSarif(f"{at}: conflicting rule references")
            ref[inner] = result[outer]
    component_ref = obj(ref.pop("toolComponent", {}), at + ".rule.toolComponent")
    component = tool["driver"]
    if component_ref:
        # The default component is the driver; explicit indexes address extensions.
        if "index" in component_ref:
            component = referenced(tool.get("extensions", []), component_ref, at + ".component")
        elif "guid" in component_ref:
            component = referenced([tool["driver"]] + tool.get("extensions", []), component_ref, at + ".component")
        elif component_ref.get("name") != component.get("name"):
            raise InvalidSarif(f"{at}.component: a name alone must identify the driver")
    rules = array(component.get("rules", []), at + ".rules")
    for i, rule in enumerate(rules):
        obj(rule, f"{at}.rules[{i}]")
    # An id-only reference may describe a rule with no embedded descriptor.
    if not ref:
        return component, None, None
    if set(ref) == {"id"} and not any(id_matches(r.get("id"), ref["id"]) for r in rules):
        return component, None, string(ref["id"], at + ".ruleId")
    rule = referenced(rules, ref, at + ".rule")
    return component, rule, string(ref.get("id", rule.get("id")), at + ".rule.id")


def location_for(location, run, at, issues):
    location = obj(location, at)
    physical = obj(location.get("physicalLocation", {}), at + ".physicalLocation")
    artifact = obj(physical.get("artifactLocation", {}), at + ".artifactLocation")
    selected = {}
    if "index" in artifact:
        indexed = obj(index(artifact["index"], array(run.get("artifacts", []), at + ".artifacts"), at + ".artifactIndex"), at)
        selected = dict(obj(indexed.get("location", {}), at + ".indexedLocation"))
    for key in ("uri", "uriBaseId"):
        if key in artifact:
            if key in selected and selected[key] != artifact[key]:
                issues.append(f"{at}: explicit and indexed artifact {key} differ")
            selected[key] = artifact[key]
    uri = selected.get("uri")
    if uri is not None:
        string(uri, at + ".uri")
    base_id = selected.get("uriBaseId")
    base = None
    if base_id is not None:
        string(base_id, at + ".uriBaseId")
        bases = obj(run.get("originalUriBaseIds", {}), at + ".originalUriBaseIds")
        if base_id in bases:
            base = obj(bases[base_id], at + ".uriBase")
        else:
            issues.append(f"{at}: URI base is not embedded")
    region = obj(physical.get("region", {}), at + ".region")
    for key in ("startLine", "startColumn", "endLine", "endColumn"):
        if key in region and (type(region[key]) is not int or region[key] < 1):
            raise InvalidSarif(f"{at}.region.{key}: expected positive integer")
    return {"uri": uri, "uri_base_id": base_id, "uri_base": base,
            "region": region, "logical_locations": location.get("logicalLocations", [])}


def result_for(result, run, tool, at, issues):
    result = obj(result, at)
    message = obj(result.get("message"), at + ".message")
    if not any(isinstance(message.get(k), str) and message[k] for k in ("text", "markdown", "id")):
        raise InvalidSarif(f"{at}.message: requires text, markdown or id")
    if "text" not in message and "markdown" not in message:
        issues.append(f"{at}: message-string lookup is unsupported; message id retained")
    component, rule, rule_id = rule_for(result, tool, at)
    kind = enum(result.get("kind", "fail"), KINDS, at + ".kind")
    explicit = result.get("level")
    if "level" in result:
        enum(explicit, LEVELS, at + ".level")
    if kind != "fail" and explicit not in (None, "none"):
        raise InvalidSarif(f"{at}: non-fail result cannot have a failure level")
    if kind != "fail":
        level, level_source = "none", "kind"
    elif explicit is not None:
        level, level_source = explicit, "result"
    elif any(i.get("ruleConfigurationOverrides") for i in run.get("invocations", [])):
        level, level_source = None, "unresolved-override"
    else:
        configuration = obj((rule or {}).get("defaultConfiguration", {}), at + ".defaultConfiguration")
        level = enum(configuration.get("level", "warning"), LEVELS, at + ".defaultLevel")
        level_source = "rule" if "level" in configuration else "sarif-default"
    baseline = result.get("baselineState")
    if "baselineState" in result:
        enum(baseline, BASELINES, at + ".baselineState")
    suppressions = array(result.get("suppressions", []), at + ".suppressions")
    for i, suppression in enumerate(suppressions):
        suppression = obj(suppression, f"{at}.suppressions[{i}]")
        enum(suppression.get("kind"), {"inSource", "external"}, at + ".suppression.kind")
        if "status" in suppression:
            enum(suppression["status"], {"accepted", "underReview", "rejected"}, at + ".suppression.status")
    return {"id": at, "rule_id": rule_id, "rule_name": (rule or {}).get("name"),
            "component": component["name"], "kind": kind, "level": level,
            "level_source": level_source, "message": message,
            "locations": [location_for(loc, run, f"{at}.locations[{i}]", issues)
                          for i, loc in enumerate(array(result.get("locations", []), at + ".locations"))],
            "baseline_state": baseline, "suppressions": suppressions,
            "fingerprints": obj(result.get("fingerprints", {}), at + ".fingerprints"),
            "partial_fingerprints": obj(result.get("partialFingerprints", {}), at + ".partialFingerprints"),
            "triage_status": "needs-validation"}


def review_log(log):
    """Structural validation of the supported subset, not full JSON-schema validation."""
    log = obj(log, "log")
    if log.get("version") != "2.1.0":
        raise InvalidSarif("log.version: this reader accepts SARIF 2.1.0 only")
    runs = array(log.get("runs"), "log.runs")
    output, issues = [], []
    if not runs:
        issues.append("log: no runs available")
    if log.get("inlineExternalProperties"):
        issues.append("log: inline external properties are unsupported")
    for n, run in enumerate(runs):
        at = f"runs[{n}]"
        run = obj(run, at)
        tool = obj(run.get("tool"), at + ".tool")
        driver = obj(tool.get("driver"), at + ".tool.driver")
        string(driver.get("name"), at + ".tool.driver.name")
        for i, component in enumerate(array(tool.get("extensions", []), at + ".extensions")):
            string(obj(component, at).get("name"), f"{at}.extensions[{i}].name")
        run_issues = []
        if run.get("externalPropertyFileReferences"):
            run_issues.append(f"{at}: external properties are unsupported and were not loaded")
        invocations = array(run.get("invocations", []), at + ".invocations")
        states, invocation_evidence = [], []
        for i, invocation in enumerate(invocations):
            invocation = obj(invocation, f"{at}.invocations[{i}]")
            success = invocation.get("executionSuccessful")
            if success is not None and type(success) is not bool:
                raise InvalidSarif(f"{at}.invocations[{i}]: executionSuccessful must be Boolean")
            if "exitCode" in invocation and type(invocation["exitCode"]) is not int:
                raise InvalidSarif(f"{at}.invocations[{i}]: exitCode must be an integer")
            states.append(success)
            notifications = {}
            for category in ("toolExecutionNotifications", "toolConfigurationNotifications"):
                entries = array(invocation.get(category, []), f"{at}.invocations[{i}].{category}")
                notifications[category] = entries
                for notification in entries:
                    notification = obj(notification, at + ".notification")
                    if "level" not in notification and "descriptor" in notification:
                        run_issues.append(f"{at}.invocations[{i}]: notification descriptor severity inheritance is unsupported")
                        continue
                    level = enum(notification.get("level", "warning"), LEVELS, at + ".notification.level")
                    if level == "error":
                        run_issues.append(f"{at}.invocations[{i}]: scanner reports an error notification")
            invocation_evidence.append({"execution_successful": success, "exit_code": invocation.get("exitCode"),
                                        "notifications": notifications})
            for field, description in (("ruleConfigurationOverrides", "rule"),
                                       ("notificationConfigurationOverrides", "notification")):
                if invocation.get(field):
                    array(invocation[field], at + "." + field)
                    run_issues.append(f"{at}.invocations[{i}]: {description} configuration overrides are unsupported")
        execution = "failed" if False in states else "succeeded" if states and all(s is True for s in states) else "unknown"
        if execution != "succeeded":
            run_issues.append(f"{at}: scanner execution {execution}; results do not establish a successful scan")
        results = run.get("results")
        if results is None:
            run_issues.append(f"{at}: results are absent or null, not a zero-finding scan")
            results = []
        findings = [result_for(r, run, tool, f"{at}.results[{i}]", run_issues)
                    for i, r in enumerate(array(results, at + ".results"))]
        output.append({"index": n, "tool": driver["name"], "tool_version": driver.get("version"),
                       "execution": execution, "invocations": invocation_evidence, "result_count": len(findings),
                       "findings": findings, "diagnostics": run_issues})
        issues.extend(run_issues)
    return {"ledger_version": 1, "sarif_version": "2.1.0", "complete": not issues,
            "interpretation": "scanner reports are candidates, not confirmed vulnerabilities",
            "run_count": len(output), "result_count": sum(r["result_count"] for r in output),
            "runs": output, "diagnostics": issues}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidSarif("JSON object contains duplicate keys")
        result[key] = value
    return result


def invalid_constant(value):
    raise InvalidSarif("JSON contains a nonfinite numeric constant")


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise InvalidSarif("JSON number exceeds the finite floating-point range")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local SARIF 2.1.0 JSON file; never a URL")
    args = parser.parse_args(argv)
    try:
        with args.input.open("rb") as stream:
            content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise InvalidSarif("input exceeds the 20 MiB local-reader limit")
        log = json.loads(content.decode("utf-8"), object_pairs_hook=unique_object,
                         parse_constant=invalid_constant, parse_float=finite_float)
        ledger = review_log(log)
        ledger["source_file"] = str(args.input)
        ledger["source_sha256"] = hashlib.sha256(content).hexdigest()
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        print(json.dumps({"ledger_version": 1, "complete": False, "error": str(error)}))
        return 2
    print(json.dumps(ledger, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if ledger["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
