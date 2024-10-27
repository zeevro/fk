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
