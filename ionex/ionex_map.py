from collections import namedtuple

from .exceptions import IONEXMapError

Grid = namedtuple('Grid', ['latitude', 'longitude'])
Latitude = namedtuple('Latitude', ['lat1', 'lat2', 'dlat'])
Longitude = namedtuple('Longitude', ['lon1', 'lon2', 'dlon'])


class IonexMap:
    """Класс карты IONEX. Содержит карту и мета-данные.

    Атрибуты:

    :type grid: namedtuple
    :param grid: определение сетки для карты, содержит два
        ``namedtupla``:

        - ``grid.latittude`` =
          ``namedtuple('Latitude', ['lat1', 'lat2', 'dlat'])`` определение
          сетки по широте от ``lat1`` до ``lat2`` с шагом ``dlat``;

        - ``grid.longitude`` =
          ``namedtuple('Longitude', ['lon1', 'lon2', 'dlon'])``
          определение сетки по долготе от ``lon1`` до ``lon2`` с шагом
          ``dlon``.

    :type tec: list
    :param tec: данные ПЭС; одномерный список, представляет собой
        набор широтных "срезов" со значениями ПЭС.

        Начало каждого среза соответствует широте ``grid.latitude.lat1``, конец
        -- ``grid.latitude.lat2``, с шагом, равным
        ``grid.latitude.dlat``.

        Долгота первого среза соответствует ``grid.longitude.lon1``, долгота
        последнего -- ``grid.longitude.lon2``, с шагом, равным
        ``grid.longitude.dlon``.

    :type height: float
    :param height: высота, с которой ассоциированы данные карты.

    :type epoch: datetime
    :param epoch: дата и время карты ПЭС.
    """

    def __init__(self, *,
                 exponent,
                 epoch,
                 longitude,
                 latitude,
                 height,
                 tec,
                 rms=None,
                 none_value=None):
        """
        :param exponent:
            ``int``, значение 'EXPONENT' из файла IONEX; степень,
            в которую будут возведены значения ПЭС.

        :param epoch:
            ``datetime.datetime``, дата и время текущей карты.

        :param longitude:
            ``tuple``, определение сетки по широте, (lon1, lon2, dlon),
            предполагается, что значения совпадают со значениями заголовка
            'LON1 / LON2 / DLON' из файла IONEX.

        :param latitude:
           ``tuple``, определение сетки по широте, (lat1, lat2, dlat),
           предполагается, что значения совпадают со значениями заголовка
           'LAT1 / LAT2 / DLAT' из файла IONEX.

        :param height:
            ``float``, высота текущей карты.

        :param tec:
            ``list``, список значений ПЭС из файла IONEX.

        :param rms:
            ``list``, список значений RMS из файла IONEX.

        :param none_value:
            ``int``, значения в карте, равные ``none_value`` будут заменены на
            ``None``. По умолчанию ``none_value`` == None, в таком случае
            никакие замены производится не будут.
        """
        self.epoch = epoch
        self.height = height
        self.grid = Grid(
            latitude=Latitude(*latitude),
            longitude=Longitude(*longitude),
        )

        self._exponent = exponent
        self._none_value = none_value

        self._tec = tec.copy()
        self._rms = rms.copy() if rms is not None else None

        if not self._grid_match_data():
            err_msg = 'The grid definition does ' \
                      'not match the map; epoch {}.'.format(self.epoch)
            raise IONEXMapError(err_msg)

    @property
    def tec(self):
        """Вернуть ПЭС с учётом степени."""
        tec = [v * 10 ** self._exponent for v in self._tec]
        if self._none_value is None:
            return tec

        none_value = self._none_value * 10 ** self._exponent
        while True:
            try:
                i = tec.index(none_value)
                tec[i] = None
            except ValueError:
                break
        return tec

    @property
    def rms(self):
        raise NotImplementedError

    def _grid_match_data(self):
        def cells(start, stop, step):
            return (abs(start) + abs(stop)) / abs(step) + 1

        lat_cells = cells(*self.grid.latitude)
        lon_cells = cells(*self.grid.longitude)
        return lon_cells * lat_cells == len(self._tec)
