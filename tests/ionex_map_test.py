from datetime import datetime

from pytest import raises, mark, approx

from ionex.ionex_map import IonexMap
from ionex.exceptions import IONEXMapError


@mark.parametrize('exp,epoch,lon,lat,height,tec', [
    (-1, datetime.now(),
     (-2.5, 2.5, 0.5), (-1.5, 1.5, 0.5), 300, list(range(0, 11)) * 7),
    (1, datetime.now(), (-8, 8, 2), (-2, 2, 1), 450, list(range(1, 10)) * 5),
])
def test_init(exp, epoch, lon, lat, height, tec):
    orig_tec = tec.copy()

    ionex_map = IonexMap(
        exponent=exp,
        epoch=epoch,
        longitude=lon,
        latitude=lat,
        height=height,
        tec=tec,
    )

    assert ionex_map.grid.longitude == lon
    assert ionex_map.grid.latitude == lat
    assert ionex_map.height == height
    assert ionex_map.tec == [v * 10 ** exp for v in tec]
    assert ionex_map.epoch == epoch

    with raises(NotImplementedError):
        rms = ionex_map.rms

    # оригинальный список не изменился
    assert tec == orig_tec


@mark.parametrize('tec,lon,lat', [
    (list(range(0, 12)) * 7, (-2.5, 2.5, 0.5), (-1.5, 1.5, 0.5)),
    (list(range(1, 10)) * 5, (-8, 8, 2), (-3, 3, 1)),
])
def test_gird_not_match_data(tec, lon, lat):
    """карта не соответствует сетке"""
    with raises(IONEXMapError):
        IonexMap(
            exponent=-1,
            epoch=datetime.now(),
            longitude=lon,
            latitude=lat,
            height=300,
            tec=tec,
        )


@mark.parametrize('none_value,exponent,in_tec,out_tec', [
    (None, 0, [1, 2, 3, 4, 9999, 6, 7, 8, 9], [1, 2, 3, 4, 9999, 6, 7, 8, 9]),
    (9999, 0, [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9]),
    (9999, 0, [1, 2, 3, 4, 9999, 6, 7, 8, 9], [1, 2, 3, 4, None, 6, 7, 8, 9]),
    (8888, 1,
     [1, 8888, 3, 4, 5, 6, 7, 8, 9],
     [10, None, 30, 40, 50, 60, 70, 80, 90]),
    (9999, -1,
     [1, 2, 3, 9999, 5, 6, 9999, 8, 9],
     [0.1, 0.2, 0.3, None, 0.5, 0.6, None, 0.8, 0.9]),
])
def test_none_value(none_value, exponent, in_tec, out_tec):
    inx = IonexMap(
        exponent=exponent,
        epoch=datetime.now(),
        longitude=(-1, 1, 1),
        latitude=(-1, 1, 1),
        height=300.,
        tec=in_tec,
        none_value=none_value,
    )
    assert out_tec == approx(inx.tec, nan_ok=True)
