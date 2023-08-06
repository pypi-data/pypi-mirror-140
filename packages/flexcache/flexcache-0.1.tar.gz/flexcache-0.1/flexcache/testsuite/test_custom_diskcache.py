import pytest

import flexcache
from flexcache import DiskCache


def test_register(tmp_path):
    c = DiskCache(tmp_path)

    class Header(flexcache.MinimumHeader):
        @classmethod
        def from_int(cls, source, reader_id):
            return cls(bytes(source), reader_id)

    c.register_header_class(int, Header.from_int)

    c.load(3)

    with pytest.raises(TypeError):
        c.load(3j)


def test_missing_cache_path(tmp_path):
    c = DiskCache(tmp_path)

    hdr = flexcache.MinimumHeader("123", "456")
    assert c.rawsave(hdr, "789").stem == c.cache_stem_for(hdr)
    assert c.rawload(hdr) == "789"
