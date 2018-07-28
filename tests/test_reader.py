import pytest

from ionex import _get_version_type, reader, IonexV1


@pytest.mark.parametrize('line,expected_ver,expected_type', [
    ('''\
123456.1xx          fONOSPHERE MAPS     GPS                 IONEX VERSION / TYPE
''', 123456.1, 'f'),
    ('''\
     1.0            IONOSPHERE MAPS     GPS                 IONEX VERSION / TYPE
    ''', 1.0, 'I')
])
def test_get_version_type(line, expected_ver, expected_type):
    ver, t = _get_version_type(line)
    assert ver == expected_ver
    assert t == expected_type


def test_reader(ionex_file):
    inx = reader(ionex_file)
    assert isinstance(inx, IonexV1)

    for _ in inx:
        pass

    assert inx._tec_maps_numbers == list(range(1, 13))

    # оставляем открытым
    if not isinstance(ionex_file, str):
        assert not ionex_file.closed
