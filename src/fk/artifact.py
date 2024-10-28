from collections.abc import Iterable
import platform
import re
import tarfile
from typing import IO, Self
import zipfile


class Artifact:
    def __new__(cls, filename: str, fileobj: IO[bytes]) -> Self:
        if filename.endswith('.zip'):
            typ = ZipArtifact
        elif filename.endswith(('.tar', '.tgz', '.txz', '.tbz', '.tar.gz', '.tar.xz', '.tar.bz')):
            typ = TarArtifact
        else:
            typ = Artifact
        return super().__new__(typ)

    def __init__(self, filename: str, fileobj: IO[bytes]) -> None:
        self._fileobj = fileobj
        self._filename = filename

    @property
    def members(self) -> list[str]:
        return [self._filename]

    def member(self, member: str) -> IO[bytes]:
        if member != self._filename:
            raise KeyError(member)
        return self._fileobj


class TarArtifact(Artifact):
    def __init__(self, filename: str, fileobj: IO[bytes]) -> None:
        super().__init__(filename, fileobj)
        self._tar = tarfile.TarFile.open(fileobj=fileobj)

    @property
    def members(self) -> list[str]:
        return self._tar.getnames()

    def member(self, member: str) -> IO[bytes]:
        f = self._tar.extractfile(member)
        if f is None:
            raise KeyError(member)
        return f


class ZipArtifact(Artifact):
    def __init__(self, filename: str, fileobj: IO[bytes]) -> None:
        super().__init__(filename, fileobj)
        self._zip = zipfile.ZipFile(fileobj)

    @property
    def members(self) -> list[str]:
        return list(self._zip.NameToInfo)

    def member(self, member: str) -> IO[bytes]:
        return self._zip.open(member)


INVALID_SUFFIX_RE = re.compile(r'\.(json|txt|sig|((md[45]|sha(1|256|512))(sum)?))$')
GOOD_SUFFIX_RE = re.compile(r'\.(zip|t(ar\.)?[bgx]z)$')


_system = platform.system()
_arch = platform.machine()

if _system == 'Windows':
    _arch = {'AMD64': 'x86_64', 'x86': 'i686', 'ARM64': 'arm64'}[_arch]

_OS = {
    'Windows': 'win(dows)?',
    'Darwin': 'darwin|macos|osx',
    'Linux': 'linux',
}
_GOOD_OS = _OS.pop(_system)
_BAD_OS = '|'.join(fr'({s})' for s in _OS.values())

_ARCH = {
    'x86_64': r'(amd64|x86[_-]64)',
    'i686': r'i?[36]86',
    'arm64': r'(arm|aarch)64',
}
_GOOD_ARCH = _ARCH.pop(_arch)
_BAD_ARCH = '|'.join(fr'({s})' for s in _ARCH.values())

_EXTRA = {
    'Windows': 'msvc',
    'Linux': 'gnu',
}.get(_system, '')


GOOD_OS_RE = re.compile(fr'(^|[_.-])({_GOOD_OS})([_.-]|$)')
BAD_OS_RE = re.compile(fr'(^|[_.-])({_BAD_OS})([_.-]|$)')
GOOD_ARCH_RE = re.compile(fr'(^|[_.-])({_GOOD_ARCH})([_.-]|$)')
BAD_ARCH_RE = re.compile(fr'(^|[_.-])({_BAD_ARCH})([_.-]|$)')
EXTRA_RE = re.compile(fr'(^|[_.-])({_EXTRA})([_.-]|$)') if _EXTRA else re.compile('^$')


def _score_artifact(artifact: str) -> int:
    return (
        bool(INVALID_SUFFIX_RE.search(artifact)) * -1000
        + bool(GOOD_SUFFIX_RE.search(artifact)) * 10
        + bool(GOOD_OS_RE.search(artifact)) * 10
        + bool(BAD_OS_RE.search(artifact)) * -100
        + bool(GOOD_ARCH_RE.search(artifact)) * 5
        + bool(BAD_ARCH_RE.search(artifact)) * -50
        + bool(EXTRA_RE.search(artifact))
    )


def choose_artifact(artifacts: Iterable[str]) -> str:
    scored = sorted((_score_artifact(a), a) for a in artifacts)

    print(*scored, sep='\n')

    # artifacts = [a for a in artifacts if not INVALID_SUFFIX_RE.search(a)]
    # if not artifacts:
    #     raise ValueError('No suitable artifact found!')
    # if len(artifacts) == 1:
    #     return artifacts[0]

    return scored[0][1]
