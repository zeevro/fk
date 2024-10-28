# ruff: noqa: SLF001, T201
import json
import platform

from fk import artifact


def main() -> None:
    with open('assets.json', 'rb') as f:
        repos = json.load(f)

    print(f'System: {artifact._system} ({platform.system()})')
    print(f'Architecture: {artifact._arch} ({platform.machine()})')
    print()
    print(f'INVALID_SUFFIX_RE: {artifact.INVALID_SUFFIX_RE.pattern} = -1000')
    print(f'GOOD_SUFFIX_RE: {artifact.GOOD_SUFFIX_RE.pattern} = +10')
    print()
    print(f'GOOD_OS_RE: {artifact.GOOD_OS_RE.pattern} = +10')
    print(f'BAD_OS_RE: {artifact.BAD_OS_RE.pattern} = -100')
    print(f'GOOD_ARCH_RE: {artifact.GOOD_ARCH_RE.pattern} = +5')
    print(f'BAD_ARCH_RE: {artifact.BAD_ARCH_RE.pattern} = -50')
    print(f'EXTRA_RE: {artifact.EXTRA_RE.pattern} = +1')
    print()

    for repo in repos:
        artifacts = {a['name'] for a in repo['assets']}
        print(f'URL: {repo["url"]}', *sorted(((artifact._score_artifact(a), a) for a in artifacts), reverse=True)[:3], '', sep='\n')


if __name__ == '__main__':
    main()
