#!/usr/bin/env python3
"""Offline design recipe search, draft briefs, and opaque sRGB pair checks."""
import argparse
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / 'assets' / 'design-recipes.json'
THRESHOLDS = {'normal': 4.5, 'large': 3.0, 'ui': 3.0}
STOP_WORDS = {'a', 'an', 'and', 'app', 'application', 'build', 'create', 'design', 'for',
              'i', 'in', 'interface', 'my', 'of', 'the', 'to', 'ui', 'want', 'web', 'with'}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    return value


def strings(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f'{label} must be a nonempty list')
    for item in value:
        text(item, label)
    return value


def rgb(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', value):
        raise ValueError('Supported colors are opaque sRGB #RGB or #RRGGBB only')
    raw = value[1:]
    if len(raw) == 3:
        raw = ''.join(char * 2 for char in raw)
    return tuple(int(raw[index:index + 2], 16) / 255 for index in (0, 2, 4))


def luminance(value):
    channels = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb(value)]
    return sum(v * weight for v, weight in zip(channels, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background, kind='normal'):
    if kind not in THRESHOLDS:
        raise ValueError(f'Unknown contrast kind: {kind}')
    low, high = sorted((luminance(foreground), luminance(background)))
    ratio = (high + 0.05) / (low + 0.05)
    return {'foreground': foreground, 'background': background, 'kind': kind,
            'ratio': ratio, 'threshold': THRESHOLDS[kind], 'passes': ratio >= THRESHOLDS[kind]}


def pairs(recipe):
    result = []
    for pair in recipe['contrast_pairs']:
        fg, bg, kind = pair['foreground'], pair['background'], pair['kind']
        checked = contrast(recipe['palette'][fg], recipe['palette'][bg], kind)
        result.append({'foreground_role': fg, 'background_role': bg, **checked})
    return result


def load_corpus(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f'Cannot read corpus: {error}') from error
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Corpus schema_version must be 1')
    sources = data.get('sources')
    if not isinstance(sources, list) or not sources:
        raise ValueError('Corpus sources must be a nonempty list')
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Each source must be an object')
        for key in ('id', 'url', 'observed', 'section', 'rights'):
            text(source.get(key), f'source.{key}')
        if source['id'] in source_ids:
            raise ValueError(f'Duplicate source ID: {source["id"]}')
        if not re.fullmatch(r'https://[^\s]+', source['url']):
            raise ValueError('Source URL must use HTTPS')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', source['observed']):
            raise ValueError('Source observation must be YYYY-MM-DD')
        date.fromisoformat(source['observed'])
        source_ids.add(source['id'])
    recipes = data.get('recipes')
    if not isinstance(recipes, list) or not recipes:
        raise ValueError('Corpus recipes must be a nonempty list')
    ids = set()
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise ValueError('Each recipe must be an object')
        for key in ('id', 'title', 'summary', 'use_when', 'avoid_when', 'rationale'):
            text(recipe.get(key), f'recipe.{key}')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', recipe['id']) or recipe['id'] in ids:
            raise ValueError(f'Invalid or duplicate recipe ID: {recipe["id"]}')
        ids.add(recipe['id'])
        for key in ('tags', 'composition', 'sources'):
            strings(recipe.get(key), f'{recipe["id"]}.{key}')
        if not set(recipe['sources']) <= source_ids:
            raise ValueError(f'Unknown source in {recipe["id"]}')
        roles = recipe.get('type_roles')
        if not isinstance(roles, dict) or not {'heading', 'body', 'data'} <= roles.keys():
            raise ValueError(f'{recipe["id"]} needs heading/body/data type roles')
        for value in roles.values():
            text(value, 'type role')
        palette = recipe.get('palette')
        if not isinstance(palette, dict) or not {'surface', 'text', 'accent', 'on_accent'} <= palette.keys():
            raise ValueError(f'{recipe["id"]} has incomplete palette roles')
        for value in palette.values():
            rgb(value)
        checked_pairs = recipe.get('contrast_pairs')
        if not isinstance(checked_pairs, list) or not checked_pairs:
            raise ValueError(f'{recipe["id"]} needs contrast pairs')
        for pair in checked_pairs:
            if not isinstance(pair, dict) or set(pair) != {'foreground', 'background', 'kind'}:
                raise ValueError('Each contrast pair needs foreground/background/kind')
            if pair['foreground'] not in palette or pair['background'] not in palette:
                raise ValueError('Contrast pair names an unknown palette role')
            if pair['kind'] not in THRESHOLDS:
                raise ValueError('Contrast pair kind must be normal, large, or ui')
        if not all(pair['passes'] for pair in pairs(recipe)):
            raise ValueError(f'{recipe["id"]} has a failing declared contrast pair')
    return data


def terms(value):
    return set(re.findall(r'[a-z0-9]+', value.lower())) - STOP_WORDS


def search(data, query, limit):
    query_terms = terms(query)
    results = []
    # Shared instructions, rationale and accessibility prose do not affect relevance.
    documents = [(r, terms(' '.join([r['id'], r['title'], *r['tags']]))) for r in data['recipes']]
    for recipe, words in documents:
        matched = sorted(words & query_terms)
        if not matched:
            continue
        score = sum(math.log(1 + len(documents) / sum(term in w for _, w in documents)) for term in matched)
        if query.strip().lower() == recipe['id']:
            score += len(documents)
        results.append({'id': recipe['id'], 'title': recipe['title'], 'matched_terms': matched,
                        'score': score, 'recipe': recipe, 'contrast': pairs(recipe)})
    results.sort(key=lambda result: (-result['score'], result['id']))
    results = results[:limit]
    used = {source for result in results for source in result['recipe']['sources']}
    return {'query': query, 'status': 'matched' if results else 'no-match', 'results': results,
            'sources': [source for source in data['sources'] if source['id'] in used],
            'limits': ['Original design candidates, not measured usability or industry-optimal recommendations.',
                       'Use existing accepted design rules and tokens before these candidates.',
                       'Pair checks cover declared opaque sRGB colors only, not rendered accessibility.']}


def markdown(result, draft):
    lines = ['# Draft design brief' if draft else '# Design recipe search', '', f'Query: {result["query"]}', '',
             f'Status: {result["status"]}', '']
    if not result['results']:
        lines += ['No corpus match. Use product evidence or research a fitting reference; no default was selected.', '']
    for item in result['results']:
        recipe = item['recipe']
        lines += [f'## {recipe["title"]} ({recipe["id"]})', '', recipe['summary'], '',
                  f'Use when: {recipe["use_when"]}', f'Avoid when: {recipe["avoid_when"]}',
                  f'Reason: {recipe["rationale"]}', '', 'Composition:', '']
        lines += [f'- {part}' for part in recipe['composition']]
        lines += ['', 'Type roles:', '']
        lines += [f'- {role}: {value}' for role, value in recipe['type_roles'].items()]
        lines += ['', 'Candidate color roles:', '']
        lines += [f'- {role}: {value}' for role, value in recipe['palette'].items()]
        lines += ['', 'Declared pair checks (unrounded ratios):', '']
        for pair in item['contrast']:
            lines.append(f'- {pair["foreground_role"]} on {pair["background_role"]}: '
                         f'{pair["ratio"]!r}:1, threshold {pair["threshold"]}, '
                         f'{"PASS" if pair["passes"] else "FAIL"} ({pair["kind"]})')
        lines += ['', 'Sources: ' + ', '.join(recipe['sources']), '']
    if draft:
        lines += ['## Product mapping still required', '',
                  '- Map candidate roles onto accepted token names; keep existing decisions and exceptions.',
                  '- Select real content, supported widths/themes and required interaction states.',
                  '- Verify geometry, actual fonts, contrast, focus and meaningful actions in the running app.', '']
    lines += ['## Limits', '', *[f'- {value}' for value in result['limits']], '', '## Sources', '']
    lines += [f'- {s["id"]}: {s["url"]} ({s["section"]}; observed {s["observed"]}; {s["rights"]})'
              for s in result['sources']]
    return '\n'.join(lines) + '\n'


def emit(content, output):
    if output:
        # Exclusive creation also preserves a concurrent writer's accepted output.
        with Path(output).open('x', encoding='utf-8') as handle:
            handle.write(content)
    else:
        sys.stdout.write(content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, default=DEFAULT_CORPUS)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('search', 'draft'):
        command = commands.add_parser(name)
        command.add_argument('query')
        command.add_argument('--limit', type=int, choices=range(1, 13), default=3 if name == 'search' else 1)
        command.add_argument('--format', choices=('json', 'markdown'), default='json' if name == 'search' else 'markdown')
        command.add_argument('--output', type=Path)
    command = commands.add_parser('contrast')
    command.add_argument('foreground')
    command.add_argument('background')
    command.add_argument('--kind', choices=tuple(THRESHOLDS), default='normal')
    commands.add_parser('validate')
    args = parser.parse_args(argv)
    try:
        if args.command == 'contrast':
            result = contrast(args.foreground, args.background, args.kind)
            print(json.dumps(result, indent=2, allow_nan=False))
            return 0 if result['passes'] else 1
        data = load_corpus(args.corpus)
        if args.command == 'validate':
            print(json.dumps({'status': 'valid', 'recipes': len(data['recipes']), 'sources': len(data['sources'])}))
            return 0
        result = search(data, args.query, args.limit)
        if args.command == 'draft':
            result['artifact'] = 'draft-design-brief'
            result['accepted'] = False
            result['mapping_required'] = ['Existing token roles', 'Real content and states', 'Rendered verification']
        content = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n' if args.format == 'json' else markdown(result, args.command == 'draft')
        emit(content, args.output)
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        print(f'design-reference: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
