from __future__ import annotations
import astrometry_extension
import collections
import dataclasses
import logging
import math
import os
import pathlib
import requests
import threading
import typing
from .wcs import Wcs

DOWNLOAD_SUFFIX = ".download"
TIMEOUT = 60.0
CHUNK_SIZE = 1048576
DEFAULT_ARCSEC_PER_PIXEL_LOWER = 0.1
DEFAULT_ARCSEC_PER_PIXEL_UPPER = 1000.0


def run(session: requests.Session, task: tuple[str, pathlib.Path]):
    url, path = task
    logging.info(f'downloading "{url}" to "{path}"')
    download_path = pathlib.Path(f"{path}{DOWNLOAD_SUFFIX}")
    response: typing.Optional[requests.Response] = None
    mode = "wb"
    if download_path.is_file():
        response = session.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            headers={"Range": f"bytes={download_path.stat().st_size}-"},
        )
        if response.status_code == 206:
            mode = "ab"
        else:
            logging.info(f'range request failed for "{url}" ({response.status_code})')
            response = None
    if response is None:
        response = session.get(
            url,
            timeout=TIMEOUT,
            stream=True,
        )
        response.raise_for_status()
    with open(download_path, mode) as download_file:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            download_file.write(chunk)
    response.close()
    download_path.rename(path)


def worker_target(queue: collections.deque):
    with requests.Session() as session:
        while True:
            try:
                run(session=session, task=queue.popleft())
            except IndexError:
                break


@dataclasses.dataclass
class Series:
    description: str
    scale_to_count: dict[int, int]
    url_pattern: str

    def scales(self, minimum: int = 0):
        return set(scale for scale in self.scale_to_count.keys() if scale >= minimum)

    def index_files(
        self,
        directory: typing.Union[bytes, str, os.PathLike],
        scales: typing.Optional[set[int]] = None,
    ) -> list[pathlib.Path]:
        if isinstance(directory, bytes):
            directory = pathlib.Path(directory.decode()).resolve()
        elif isinstance(directory, str):
            directory = pathlib.Path(directory).resolve()
        else:
            directory = pathlib.Path(directory)
        assert isinstance(directory, pathlib.Path)
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=True)
        if scales is None:
            scales = set(self.scale_to_count.keys())
        urls: list[str] = []
        paths: list[pathlib.Path] = []
        for scale in scales:
            count = self.scale_to_count[scale]
            if count == 1:
                url = self.url_pattern.format(scale=f"{scale:02d}", index="")
                urls.append(url)
                paths.append(directory / url.rsplit("/", 1)[1])
            else:
                for index in range(0, count):
                    url = self.url_pattern.format(
                        scale=f"{scale:02d}", index=f"-{index:02d}"
                    )
                    urls.append(url)
                    paths.append(directory / url.rsplit("/", 1)[1])
        tasks = collections.deque()
        for url, path in zip(urls, paths):
            if not path.is_file():
                tasks.append((url, path))
        if len(tasks) == 1:
            with requests.Session() as session:
                run(session=session, task=tasks.popleft())
        elif len(tasks) > 1:
            cpu_count = os.cpu_count()
            if cpu_count is None:
                cpu_count = 8
            queue = collections.deque(tasks)
            workers = tuple(
                threading.Thread(target=worker_target, daemon=True, args=(queue,))
                for _ in range(0, min(len(tasks), cpu_count))
            )
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()
        return paths


series_4100 = Series(
    description="built from the Tycho-2 catalog, good for images wider than 1 degree, recommended",
    scale_to_count={
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 1,
        16: 1,
        17: 1,
        18: 1,
        19: 1,
    },
    url_pattern="http://data.astrometry.net/4100/index-41{scale}.fits",
)

series_4200 = Series(
    description="built from the near-infared 2MASS survey, runs out of stars at the low end, most users will probably prefer series_4100 or series_5200",
    scale_to_count={
        0: 48,
        1: 48,
        2: 48,
        3: 48,
        4: 48,
        5: 12,
        6: 12,
        7: 12,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 1,
        16: 1,
        17: 1,
        18: 1,
        19: 1,
    },
    url_pattern="http://data.astrometry.net/4200/index-42{scale}{index}.fits",
)

series_5000 = Series(
    description="an older version from Gaia-DR2 but without Tycho-2 stars merged in, our belief is that series_5200 will work better than this one",
    scale_to_count={0: 48, 1: 48, 2: 48, 3: 48, 4: 48, 5: 12, 6: 12, 7: 12},
    url_pattern="http://data.astrometry.net/5000/index-50{scale}{index}.fits",
)

series_5200 = Series(
    description="LIGHT version built from Tycho-2 + Gaia-DR2, good for images narrower than 1 degree, combine with 4100-series for broader scale coverage, the LIGHT version contains smaller files with no additional Gaia-DR2 information tagged along, recommended",
    scale_to_count={0: 48, 1: 48, 2: 48, 3: 48, 4: 48, 5: 48, 6: 48},
    url_pattern="https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/index-52{scale}{index}.fits",
)

series_5200_heavy = Series(
    description="HEAVY version same as series_5200, but with additional Gaia-DR2 information (magnitude in G, BP, RP, proper motions and parallaxes), handy if you want that extra Gaia information for matched stars",
    scale_to_count={0: 48, 1: 48, 2: 48, 3: 48, 4: 48, 5: 48, 6: 48},
    url_pattern="https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/index-52{scale}{index}.fits",
)

series_6000 = Series(
    description="very specialized, uses GALEX Near-UV measurements, and only a narrow range of scales",
    scale_to_count={4: 12, 5: 12, 6: 12},
    url_pattern="http://data.astrometry.net/6000/index-60{scale}{index}.fits",
)

series_6100 = Series(
    description="very specialized, uses GALEX Far-UV measurements, and only a narrow range of scales",
    scale_to_count={4: 12, 5: 12, 6: 12},
    url_pattern="http://data.astrometry.net/6000/index-61{scale}{index}.fits",
)


@dataclasses.dataclass
class PositionHint:
    deg_ra: float
    deg_dec: float
    deg_radius: float

    def __post_init__(self):
        assert self.deg_ra >= 0.0 and self.deg_ra < 360.0
        assert self.deg_dec >= -90.0 and self.deg_dec <= 90.0
        assert self.deg_radius >= 0


@dataclasses.dataclass
class SizeHint:
    arcsec_per_pixel_lower: float
    arcsec_per_pixel_upper: float

    def __post_init__(self):
        assert self.arcsec_per_pixel_lower > 0
        assert self.arcsec_per_pixel_upper > 0
        assert self.arcsec_per_pixel_lower <= self.arcsec_per_pixel_upper


@dataclasses.dataclass
class Solution:
    logodds: float


class Solver(astrometry_extension.Solver):
    def __init__(self, index_files: list[pathlib.Path]):
        super().__init__([str(path.resolve()) for path in index_files])
        self.solve_id_lock = threading.Lock()
        self.solve_id = 0

    def solve(
        self,
        stars_xs: list[float],
        stars_ys: list[float],
        stars_fluxes: typing.Optional[list[float]],
        stars_backgrounds: typing.Optional[list[float]],
        size_hint: typing.Optional[SizeHint],
        position_hint: typing.Optional[PositionHint],
        solve_id: typing.Optional[str] = None,
        print_logodds_threshold: float = math.log(1e6),
        keep_logodds_threshold: float = math.log(1e9),
        tune_logodds_threshold: float = math.log(1e6),
    ) -> typing.Optional[Solution]:
        with self.solve_id_lock:
            self.solve_id += 1
        if size_hint is None:
            size_hint = SizeHint(
                arcsec_per_pixel_lower=DEFAULT_ARCSEC_PER_PIXEL_LOWER,
                arcsec_per_pixel_upper=DEFAULT_ARCSEC_PER_PIXEL_UPPER,
            )
        raw_solution = super().solve(
            stars_xs,
            stars_ys,
            stars_fluxes,
            stars_backgrounds,
            size_hint.arcsec_per_pixel_lower,
            size_hint.arcsec_per_pixel_upper,
            None
            if position_hint is None
            else (
                position_hint.deg_ra,
                position_hint.deg_dec,
                position_hint.deg_radius,
            ),
            str(self.solve_id) if solve_id is None else solve_id,
            print_logodds_threshold,
            keep_logodds_threshold,
            tune_logodds_threshold,
        )
        return raw_solution
