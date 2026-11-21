#!/usr/bin/env python3
"""Score point and quantile forecasts per fold against a naive or seasonal-naive baseline.

Input JSON (see assets/forecasts.json). Output JSON on stdout.
Exit 0 when every fold is evaluated, 1 when any fold failed, 2 on invalid input.
"""
import argparse
import json
import math
from pathlib import Path
import sys

FOLD_FIELDS = {"fold", "train", "actual", "point"}


class InputError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, json.dumps({"error": "invalid arguments: " + message}) + "\n")


def require(condition, message):
    if not condition:
        raise InputError(message)


def numbers(value, label, allow_empty=False):
    require(isinstance(value, list) and (allow_empty or value), label + ": expected a nonempty list")
    for item in value:
        require(type(item) in (int, float) and math.isfinite(item), label + ": expected finite numbers")
    return value


def load(path):
    def unique(pairs):
        keys = [k for k, _ in pairs]
        require(len(keys) == len(set(keys)), "duplicate JSON key")
        return dict(pairs)

    def reject(_):
        raise InputError("nonfinite JSON number")

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=reject)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise InputError("cannot read a valid UTF-8 JSON input file") from None
    require(isinstance(data, dict) and set(data) == {"schema_version", "season_length", "quantiles", "folds"},
            "expected exactly schema_version, season_length, quantiles, folds")
    require(data["schema_version"] == 1 and type(data["schema_version"]) is int, "unsupported schema_version")
    m = data["season_length"]
    require(type(m) is int and m >= 1, "season_length must be an integer >= 1 (1 means naive)")
    quantiles = numbers(data["quantiles"], "quantiles", allow_empty=True)
    require(all(0 < q < 1 for q in quantiles) and len(set(quantiles)) == len(quantiles),
            "quantiles must be distinct values in (0, 1)")
    require(isinstance(data["folds"], list) and data["folds"], "folds must be a nonempty list")
    names = set()
    for index, fold in enumerate(data["folds"]):
        label = "fold %d" % index
        require(isinstance(fold, dict) and FOLD_FIELDS <= set(fold) <= FOLD_FIELDS | {"quantile_forecasts"},
                label + ": unexpected or missing fields")
        require(isinstance(fold["fold"], str) and fold["fold"] not in names, label + ": fold ids must be unique text")
        names.add(fold["fold"])
        numbers(fold["train"], label + " train")
        numbers(fold["actual"], label + " actual")
        numbers(fold["point"], label + " point")
        require(len(fold["point"]) == len(fold["actual"]), label + ": point and actual lengths differ")
        given = fold.get("quantile_forecasts", {})
        require(isinstance(given, dict), label + ": quantile_forecasts must be an object")
        require(set(given) == ({str(q) for q in quantiles} if given or quantiles else set()),
                label + ": quantile_forecasts keys must match quantiles")
        for key, values in given.items():
            numbers(values, label + " quantile " + key)
            require(len(values) == len(fold["actual"]), label + ": quantile %s length differs" % key)
        ordered = [given[str(q)] for q in sorted(quantiles)] if given else []
        for lower, upper in zip(ordered, ordered[1:]):
            require(all(a <= b for a, b in zip(lower, upper)), label + ": quantile forecasts cross")
    return data


def mae(errors):
    return sum(abs(e) for e in errors) / len(errors)


def pinball(q, actual, forecast):
    return sum(max(q * (y - f), (q - 1) * (y - f)) for y, f in zip(actual, forecast)) / len(actual)


def score(fold, m, quantiles):
    train, actual, point = fold["train"], fold["actual"], fold["point"]
    if len(train) <= m:
        return {"fold": fold["fold"], "status": "failed", "reason": "train has no more than season_length values"}
    scale = mae([train[t] - train[t - m] for t in range(m, len(train))])
    if scale == 0:
        return {"fold": fold["fold"], "status": "failed",
                "reason": "in-sample seasonal-naive error is zero, so MASE is undefined"}
    naive = [train[len(train) - m + (h % m)] for h in range(len(actual))]
    result = {
        "fold": fold["fold"], "status": "evaluated", "horizon": len(actual), "scale": scale,
        "model_mase": mae([y - f for y, f in zip(actual, point)]) / scale,
        "baseline_mase": mae([y - f for y, f in zip(actual, naive)]) / scale,
    }
    result["beats_baseline"] = result["model_mase"] < result["baseline_mase"]
    given = fold.get("quantile_forecasts", {})
    if given:
        losses = {str(q): pinball(q, actual, given[str(q)]) for q in quantiles}
        result["pinball"] = losses
        result["mean_pinball"] = sum(losses.values()) / len(losses)
        low, high = min(quantiles), max(quantiles)
        if low < 0.5 < high:
            inside = [given[str(low)][i] <= y <= given[str(high)][i] for i, y in enumerate(actual)]
            result["interval"] = {
                "quantiles": [low, high], "nominal": high - low, "coverage": sum(inside) / len(inside),
                "mean_width": sum(given[str(high)][i] - given[str(low)][i] for i in range(len(actual))) / len(actual),
            }
    return result


def finite(value):
    if isinstance(value, dict):
        return all(finite(v) for v in value.values())
    if isinstance(value, list):
        return all(finite(v) for v in value)
    return not isinstance(value, float) or math.isfinite(value)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument("forecasts")
    args = parser.parse_args()
    try:
        data = load(args.forecasts)
        folds = [score(f, data["season_length"], data["quantiles"]) for f in data["folds"]]
        require(all(finite(f) for f in folds), "values too large: a score is not finite")
    except (InputError, OverflowError) as error:
        message = str(error) if isinstance(error, InputError) else "values too large to score"
        print(json.dumps({"error": message}), file=sys.stderr)
        return 2
    evaluated = [f for f in folds if f["status"] == "evaluated"]
    summary = {"folds_total": len(folds), "folds_evaluated": len(evaluated),
               "folds_failed": len(folds) - len(evaluated),
               "folds_beating_baseline": sum(1 for f in evaluated if f["beats_baseline"])}
    print(json.dumps({"command": "baseline", "season_length": data["season_length"],
                      "baseline": "naive" if data["season_length"] == 1 else "seasonal naive",
                      "summary": summary, "folds": folds,
                      "limits": ["MASE scale is the in-sample seasonal-naive error on that fold's train values.",
                                 "Interval coverage on a short horizon is a noisy estimate."]},
                     indent=2, allow_nan=False))
    return 0 if len(evaluated) == len(folds) else 1


if __name__ == "__main__":
    sys.exit(main())
