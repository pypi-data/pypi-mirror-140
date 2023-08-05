"""
datazen - A module for cache implementations, conforming to package-wide,
          data-structure constraints and assumptions.
"""

# built-in
from collections import UserDict
import logging
from pathlib import Path
from time import perf_counter_ns
from typing import Dict

# internal
from datazen.archive import extractall, make_archive
from datazen.code import ARBITER, DataArbiter
from datazen.code.types import FileExtension
from datazen.parsing import merge
from datazen.paths import get_file_name, nano_str


class FlatDirectoryCache(UserDict):
    """
    A class implementing a dictionary that can be saved and loaded from disk,
    with a specified encoding scheme.
    """

    def __init__(
        self,
        root: Path,
        initialdata: dict = None,
        archive_encoding: str = "tar.gz",
        data_encoding: str = "json",
        arbiter: DataArbiter = ARBITER,
        **load_kwargs,
    ) -> None:
        """Initialize this data cache."""

        super().__init__(initialdata)
        self.root = root
        self.archive_encoding = archive_encoding
        self.data_encoding = data_encoding
        self.arbiter = arbiter
        self.load_time_ns: int = -1
        self.save_time_ns: int = -1

        # A derived class must add logic to set this.
        self.changed: bool = False

        merge(self.data, self.load(self.root, **load_kwargs))

    def load_directory(
        self,
        path: Path,
        data: Dict[str, dict],
        **kwargs,
    ) -> int:
        """Load a directory and update data, return time taken to load."""

        start = perf_counter_ns()
        for child in path.iterdir():
            # Don't traverse directories.
            if child.is_file():
                load = self.arbiter.decode(child, **kwargs)
                key = get_file_name(child)
                assert key
                if load.success:
                    assert (
                        key not in data
                    ), f"Data for '{key}' is already loaded!"
                    data[key] = load.data

        # Return load time.
        return perf_counter_ns() - start

    def load(
        self,
        path: Path = None,
        logger: logging.Logger = None,
        level: int = logging.DEBUG,
        **kwargs,
    ) -> Dict[str, dict]:
        """Load data from disk."""

        if path is None:
            path = self.root

        loaded = False
        result: Dict[str, dict] = {}
        if path.is_dir():
            self.load_time_ns = self.load_directory(path, result, **kwargs)
            loaded = True

        # See if we can locate an archive for this path, that we can extract
        # and then load.
        else:
            archive = FileExtension.has_archive(path)
            if archive is not None:
                success, time_ns = extractall(archive, path.parent)
                if success:
                    if logger is not None:
                        logger.log(
                            level,
                            "Extracted archive '%s' in %ss.",
                            archive,
                            nano_str(time_ns),
                        )
                    return self.load(path, logger, level, **kwargs)

        if loaded and logger is not None:
            logger.log(
                level, "Cache loaded in %ss.", nano_str(self.load_time_ns)
            )
        return result

    def save_directory(self, path: Path, **kwargs) -> int:
        """Write data in this cache to a directory."""

        start = perf_counter_ns()
        path.mkdir(parents=True, exist_ok=True)
        for key, val in self.data.items():
            assert self.arbiter.encode(
                Path(path, f"{key}.{self.data_encoding}"), val, **kwargs
            )[0], f"Couldn't write key '{key}' to cache ({path})!"

        return perf_counter_ns() - start

    def save(
        self,
        path: Path = None,
        logger: logging.Logger = None,
        level: int = logging.DEBUG,
        archive: bool = False,
        **kwargs,
    ) -> None:
        """Save data to disk."""

        if path is None:
            path = self.root

        if self.changed:
            self.save_time_ns = self.save_directory(path, **kwargs)

            # Create an archive for this cache as well.
            if archive:
                result = make_archive(path, self.archive_encoding)
                assert (
                    result[0] is not None
                ), "Tried to make archive but couldn't!"
                if logger is not None:
                    logger.log(
                        level,
                        "Cache archived to '%s' in %ss.",
                        result[0],
                        result[1],
                    )

        if self.changed and logger is not None:
            logger.log(
                level, "Cache written in %ss.", nano_str(self.save_time_ns)
            )
        self.changed = False
