from pathlib import Path
from typing import Any

from UE4Parse.Assets.PackageReader import LegacyPackageReader
from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Provider import DefaultFileProvider
from UE4Parse.Versions import EUEVersion, VersionContainer


def load(uasset: Path, uexp: Path) -> Any:
    provider = DefaultFileProvider([], VersionContainer(EUEVersion.GAME_UE4_19))

    package = LegacyPackageReader(
        uasset=BinaryStream(str(uasset)),
        uexp=BinaryStream(str(uexp)),
        provider=provider,
    )

    if package is None:
        raise ValueError("Something went wrong when reading the package")

    return package.get_dict()
