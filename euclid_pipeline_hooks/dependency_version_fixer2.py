#!/usr/bin/env python3
# Copyright (C) 2012-2023, UNIGE and contributors (for the Euclid Science Ground Segment)
# This file is part of Elements <https://gitlab.euclid-sgs.uk/ST-TOOLS/Elements>
# SPDX-License-Identifier: LGPL-3.0-or-later
""" Script to fix the version of a Elements-base pipeline project dependencies
    It is meant to be run in the pre-commit hook framework
"""
from __future__ import annotations

import os
import re
import argparse

from git.repo import Repo
from typing import Sequence

_TXT_PLAIN_VERSION_STYLE = r'(?:\d+)\.(?:\d+)(?:\.(?:\d+))?'
NAME_AND_VERSION = re.compile(r'(\w+)\s+(%s)' % _TXT_PLAIN_VERSION_STYLE)


def _normalize_entry(entry: str) -> str:
    return ' '.join(entry.replace('\n', ' ').strip().split())


def _filter_comments(input_text: str, comment: str='#') -> str:
    output_lines = []

    for line in input_text.splitlines():
        if not line.lstrip().startswith(comment):
            output_lines.append(line)

    return '\n'.join(output_lines)


def _get_main_entry(content: str) -> str:
    main_string = ''

    main_string_match = re.compile(r'[^#\n]*elements_project\s*\((.+?)(?=USE|DESCRIPTION|\))', re.DOTALL)

    m = main_string_match.search(content)

    if m:
        main_string = _normalize_entry(m.group(1))

    return main_string


def _get_name_and_version(content: str) -> tuple[str, str]:
    name = ''
    version = ''

    main_entry = _get_main_entry(content)

    m = NAME_AND_VERSION.match(main_entry)

    if m:
        name = m.group(1)
        version = m.group(2)

    return name, version


def _get_dependency_entry(content: str) -> str:
    use_string = ''

    use_string_match = re.compile(r'[^#\n]*elements_project\s*\(.+USE((?s:.+?))(?=DESCRIPTION|\))', re.DOTALL)

    m = use_string_match.search(content)

    if m:
        use_string = _normalize_entry(m.group(1))

    return use_string


def _get_dependencies(content: str) -> list[tuple[str, str]]:
    dependencies = []

    entry = _get_dependency_entry(content)

    m = NAME_AND_VERSION.findall(entry)

    if m:
        dependencies = m

    return dependencies


def _get_projects(content: str) -> list[tuple[str, str]]:
    projects: list[tuple[str, str]] = []

    content = _filter_comments(content)

    projects.append(_get_name_and_version(content))
    projects += _get_dependencies(content)

    return projects


def _sub(content: str, project_name: str, new_version: str, project_version: str='') -> str:

    txt_search_project = fr'({project_name})([\n\s]+|/)({_TXT_PLAIN_VERSION_STYLE})'

    if project_version:
        txt_search_project = r'({})([\n\s]+|/)({})'.format(project_name, project_version.replace('.', r'\.'))

    search_project = re.compile(txt_search_project)

    new_content = search_project.sub(r'\g<1>\g<2>%s' % new_version, content)

    return new_content


def _fix_file(filename: str, projects: list[tuple[str, str]]) -> bool:
    has_changed = False
    with open(filename) as file_processed:
        content = file_processed.read()

    new_content = content
    for project, version in projects:
        new_content = _sub(new_content, project, version)

    if content != new_content:
        with open(filename, mode='w') as file_processed:
            file_processed.write(new_content)
        has_changed = True

    return has_changed


def _is_selected(entry_path: str, filters: list[str]) -> bool:
    selected = False

    if not os.path.isdir(entry_path):
        for f in filters:
            if re.match(fr"{f}", entry_path):
                selected = True
                break

    return selected


def main(argv: Sequence[str] | None=None) -> int:
    return_code = 0

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filter',
        action='append',
        default=[],
        metavar='*|FILTER[,FILTER,...]',
        help=(
            'Filter to select files to act on  '
            'default: %(default)s'
        ),
    )

    args = parser.parse_args(argv)

    all_filters = args.filter

    # print(f'Current working directory {os.getcwd()}')

    with open('CMakeLists.txt') as cmake_list:
        content = cmake_list.read()

    projects = _get_projects(content)

    repo = Repo(os.getcwd())

    for entry in repo.commit().tree.traverse():
        entry_path = entry.path
        if _is_selected(entry_path, all_filters) and _fix_file(entry_path, projects):
            print(f'Fixing {entry_path}')
            return_code = 1

    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
