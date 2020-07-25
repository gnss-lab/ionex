from datetime import datetime
from io import StringIO

import pytest

from ionex.ionex_file import IonexV1, Grid, MapGridDef
from ionex.ionex_file import Latitude, Longitude, Height, Map


@pytest.fixture
def ionex_header():
    return StringIO('''\
     1.0            IONOSPHERE MAPS     MIX                 IONEX VERSION / TYPE
tecrms2ionex_2.awk  gAGE/UPC            11/27/07  811UT     PGM / RUN BY / DATE
  1999     1     2     1     0     0                        EPOCH OF FIRST MAP
  1999     1     2    23     0     0                        EPOCH OF LAST MAP
  7200                                                      INTERVAL
    12                                                      # OF MAPS IN FILE
  COSZ                                                      MAPPING FUNCTION
     0.0                                                    ELEVATION CUTOFF
Combined TEC calculated as weighted mean of input TEC valuesOBSERVABLES USED
     0                                                      # OF STATIONS
    27                                                      # OF SATELLITES
  6371.0                                                    BASE RADIUS
     2                                                      MAP DIMENSION
   450.0 450.0   0.0                                        HGT1 / HGT2 / DHGT
    87.5 -87.5  -2.5                                        LAT1 / LAT2 / DLAT
  -180.0 180.0   5.0                                        LON1 / LON2 / DLON
    -1                                                      EXPONENT
                                                            END OF HEADER
     1                                                      START OF TEC MAP
  1999     1     2     1     0     0                        EPOCH OF CURRENT MAP
''')


@pytest.fixture
def lat_def():
    return Latitude(87.5, -87.5, -2.5)


@pytest.fixture
def lon_def():
    return Longitude(-180.0, 180.0, 5.0)


@pytest.fixture
def hgt_def():
    return Height(450.0, 450.0, 0.0)


@pytest.fixture
def grid_def(lat_def, lon_def, hgt_def):
    return Grid(lat_def, lon_def, hgt_def)


@pytest.mark.parametrize('value, expected', [
    ('0', 0),
    ('1.0', 1),
    ('12.2', 12),
])
def test_coerce_to_int(value, expected):
    assert expected == IonexV1._coerce_into_int(value)


def test_coerce_to_int_error(ionex_file):
    inx = IonexV1(ionex_file)
    with pytest.raises(ValueError):
        inx._coerce_into_int('hello')


@pytest.mark.parametrize('epoch_str,dt', [
    ('''\
  1999     1     2     1     0     0                        EPOCH OF CURRENT MAP
''', datetime(1999, 1, 2, 1, 0, 0)),
    ('''\
  2000    12    12    11    20    15                        EPOCH OF CURRENT MAP
''', datetime(2000, 12, 12, 11, 20, 15)),
    ('''\
  2009     3     2    17    60     0                        EPOCH OF CURRENT MAP
''', datetime(2009, 3, 2, 18, 0, 0)),
    ('''\
  1996     3     9    20     0    60                        EPOCH OF CURRENT MAP
''', datetime(1996, 3, 9, 20, 1, 0)),
    ('''\
  1996     3     9    20    60    60                        EPOCH OF CURRENT MAP
''', datetime(1996, 3, 9, 21, 1, 0)),
    ('''\
  1996     3     9    20    61    73                        EPOCH OF CURRENT MAP
''', datetime(1996, 3, 9, 21, 2, 13)),
    # XXX: не все соблюдают формат
    ('''\
  2012     3     8     6     0  0.00                        EPOCH OF CURRENT MAP
''', datetime(2012, 3, 8, 6, 0, 0)),
    ('''\
  1997     4    16    24     0     0                        EPOCH OF CURRENT MAP
    ''', datetime(1997, 4, 17, 0, 0, 0)),
])
def test_parse_epoch(epoch_str, dt, ionex_file):
    inx = IonexV1(ionex_file)
    assert dt == inx._parse_epoch(epoch_str)


@pytest.mark.parametrize('grid_def_str,result', [
    ('''\
    87.5-180.0 180.0   5.0 450.0                            LAT/LON1/LON2/DLON/H
''', MapGridDef(87.5, -180., 180., 5., 450.)),
])
def test_parse_map_grid_def(grid_def_str, result):
    assert result == IonexV1._parse_map_grid_def(grid_def_str)


@pytest.mark.parametrize('line,result', [
    ('''\
   91   95   93   92   93   99  106  112  111
''', [91, 95, 93, 92, 93, 99, 106, 112, 111, ]),
    ('''\
   82   80   80   81   82   83   83   83   82   80   71   67   67   69   72   82
''', [82, 80, 80, 81, 82, 83, 83, 83, 82, 80, 71, 67, 67, 69, 72, 82, ]),
    ('''\
  864 1225 1850 2864 4459 6918106621632624853   82   85   89   94   96   94   91
''',
     [864, 1225, 1850, 2864, 4459, 6918, 10662, 16326, 24853, 82, 85,
      89, 94, 96, 94, 91]),
])
def test_read_slice(line, result):
    assert result == IonexV1._read_slice(line)


def test_read_header(ionex_header, lon_def, lat_def, hgt_def, grid_def):
    inx = IonexV1(ionex_header)
    with inx._context_manager as file_object:
        inx._read_header(file_object)

        # ожидаемые атрибуты
        assert inx.exponent == -1
        assert inx.dimension == 2

        assert inx.latitude == lat_def
        assert inx.longitude == lon_def
        assert inx.height == hgt_def

        assert inx.grid == grid_def

        # прервались сразу после заголовка
        line = next(file_object)
        assert line == (
            '     1                                                   '
            '   START OF TEC MAP\n'
        )


def test_read_map(one_map_file, one_map_file_data):
    inx = IonexV1(one_map_file)

    # FIXME: в фикстуры
    epoch = datetime(1999, 1, 2, 1, 0, 0)
    height = 450.0
    result = Map(epoch=epoch, height=height, data=one_map_file_data)

    # находимся в начале файла: промотаем до начала карты
    line = ''
    with inx._context_manager as file_object:
        for _ in range(19):
            line = next(file_object)
        assert line == '''\
     1                                                      START OF TEC MAP
'''
        assert result == inx._read_map(file_object)


def test_reader(ionex_file):
    inx = IonexV1(ionex_file)
    # имитируем чтение
    for _ in inx:
        pass
    assert inx._tec_maps_numbers == list(range(1, 13))


def test_reader_no_end_of_file(ionex_file_no_end_of_file):
    inx = IonexV1(ionex_file_no_end_of_file)
    with pytest.warns(UserWarning, match='Unexpected end of the file'):
        for _ in inx:
            pass
    assert inx._tec_maps_numbers == list(range(1, 13))
