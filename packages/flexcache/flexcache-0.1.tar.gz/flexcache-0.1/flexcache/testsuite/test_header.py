import json
import pathlib
import pickle
import time
from dataclasses import asdict as dc_asdict
from dataclasses import dataclass

import flexcache

# These sleep time is needed when run on GitHub Actions
# If not given or too short, some mtime changes are not visible.
FS_SLEEP = 0.010


def test_empty(tmp_path):
    hdr = flexcache.MinimumHeader("123", "myreader")
    assert tuple(hdr.for_cache_name()) == ("myreader".encode("utf-8"),)

    p1 = tmp_path / "cache.pickle"
    assert not hdr.is_valid(p1)
    p1.touch()
    assert hdr.is_valid(p1)
    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_basic_python():
    hdr = flexcache.BasicPythonHeader("123", "myreader")
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 4

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_content(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByFileContentHeader, flexcache.MinimumHeader):
        pass

    p = tmp_path / "source.txt"
    p.write_bytes(b"1234")
    hdr = Hdr(p, "myreader")

    assert hdr.source_path == p
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert cn[1] == b"1234"

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_path(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByPathHeader, flexcache.MinimumHeader):
        pass

    p = tmp_path / "source.txt"
    p.write_bytes(b"1234")
    hdr = Hdr(p, "myreader")

    assert hdr.source_path == p
    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert cn[1] == bytes(p.resolve())

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_name_by_paths(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByMultiplePathsHeader, flexcache.MinimumHeader):
        pass

    p0 = tmp_path / "source0.txt"
    p0.touch()

    time.sleep(FS_SLEEP)

    p1 = tmp_path / "source1.txt"
    p2 = tmp_path / "source2.txt"
    p1.write_bytes(b"1234")
    p2.write_bytes(b"1234")
    hdr = Hdr((p1, p2), "myreader")

    time.sleep(FS_SLEEP)

    p3 = tmp_path / "source3.txt"
    p3.touch()

    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 3
    assert cn[1] == bytes(p1.resolve())
    assert cn[2] == bytes(p2.resolve())

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False

    assert not hdr.is_valid(tmp_path / "not.txt")
    assert not hdr.is_valid(p0)
    assert hdr.is_valid(p3)


def test_name_by_obj(tmp_path):
    @dataclass(frozen=True)
    class Hdr(flexcache.NameByObjHeader, flexcache.MinimumHeader):
        pass

    hdr = Hdr((1, 2, 3), "myreader")

    cn = tuple(hdr.for_cache_name())
    assert len(cn) == 2
    assert hdr.pickle_protocol == pickle.HIGHEST_PROTOCOL
    assert cn[1] == pickle.dumps((1, 2, 3), hdr.pickle_protocol)

    try:
        json.dumps({k: str(v) for k, v in dc_asdict(hdr).items()})
    except Exception:
        assert False


def test_predefined_headers(tmp_path):
    fn = "source.txt"
    hdr = flexcache.DiskCacheByMTime.Header.from_string(fn, "123")
    assert isinstance(hdr.source_path, pathlib.Path)
    assert str(hdr.source_path) == fn

    hdr = flexcache.DiskCacheByHash.Header.from_string(fn, "123")
    assert isinstance(hdr.source_path, pathlib.Path)
    assert str(hdr.source_path) == fn
