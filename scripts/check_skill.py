#!/usr/bin/env python3
"""Offline checks for this package's simple metadata, local links and eval cases.

Not a general YAML/Markdown parser or a model/UI behavior evaluator.
"""
from pathlib import Path
import argparse
import json
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

REQUIRED_CASES = {'no-browser', 'brand-preservation', 'unknown-visibility', 'rewrite-chinese', 'reflow-outcomes'}


def prose(text):
    """Ignore fenced examples when finding headings and inline links."""
    lines, fence = [], None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match[1]
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            lines.append('')
        else:
            lines.append(line if fence is None else '')
    return '\n'.join(lines)


def anchors(text):
    """GitHub-style slugs for the plain headings used by this package."""
    counts, result = {}, set()
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', prose(text), re.M):
        slug = ''.join(c for c in heading.lower() if c in '-_ ' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        result.add(f'{slug}-{n}' if n else slug)
    return result


def check(root):
    root = Path(root).resolve()
    errors = []
    skill = root / 'SKILL.md'
    if not skill.is_file():
        return ['Missing SKILL.md']
    text = skill.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not match:
        errors.append('SKILL.md: missing frontmatter block')
    else:
        fields = {}
        for line in match[1].splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            field = re.fullmatch(r'([a-z][a-z-]*):\s+(.+)', line)
            if not field:
                errors.append('SKILL.md: unsupported metadata syntax (use simple key: value scalars)')
                continue
            key, value = field.groups()
            if key in fields:
                errors.append(f'SKILL.md: duplicate metadata key {key}')
            fields[key] = value
        name = fields.get('name', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
            errors.append('SKILL.md: invalid or missing name')
        description = fields.get('description', '')
        if not description.strip() or len(description) > 1024:
            errors.append('SKILL.md: invalid or missing description')
        if 'allowed-tools' in fields:
            errors.append('SKILL.md: this package must not add tool grants')
    # Checkout names can differ; installed directory naming is the installer's responsibility.
    for path in sorted(root.rglob('*.md')):
        if '.git' in path.relative_to(root).parts:
            continue
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)', prose(path.read_text(encoding='utf-8'))):
            parts = urlsplit(target.strip('<>'))
            if parts.scheme or parts.netloc:
                continue
            resolved = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not resolved.is_relative_to(root):
                errors.append(f'{path.relative_to(root)}: link escapes package: {target}')
            elif not resolved.is_file():
                errors.append(f'{path.relative_to(root)}: missing local file: {target}')
            elif parts.fragment and resolved.suffix == '.md' and unquote(parts.fragment) not in anchors(resolved.read_text(encoding='utf-8')):
                errors.append(f'{path.relative_to(root)}: missing local anchor: {target}')
    cases_path = root / 'tests/behavior_cases.json'
    try:
        cases = json.loads(cases_path.read_text(encoding='utf-8'))
        if not isinstance(cases, list):
            raise ValueError('expected an array')
        ids = []
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError('each case must be an object')
            for key in ('id', 'prompt'):
                if not isinstance(case.get(key), str) or not case[key].strip():
                    raise ValueError(f'each case needs a nonempty {key}')
            ids.append(case['id'])
            for key in ('required_behaviors', 'forbidden_behaviors'):
                values = case.get(key)
                if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                    raise ValueError(f'{case["id"]}: {key} must contain nonempty strings')
        if len(ids) != len(set(ids)):
            errors.append('Behavior cases: duplicate IDs')
        if set(ids) != REQUIRED_CASES:
            errors.append('Behavior cases: expected the five approved scenario IDs')
    except (OSError, ValueError) as exc:
        errors.append(f'Behavior cases: {exc}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print('PASS: metadata, local links/anchors, and five behavioral-case definitions.')
    print('NOT RUN: model behavior evaluation, live UI, browser or screen-reader tests.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
