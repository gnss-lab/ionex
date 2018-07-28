import warnings
from collections import namedtuple
from datetime import datetime, timedelta

from .ionex_map import IonexMap
from .exceptions import IONEXUnexpectedEnd

Grid = namedtuple('Grid', ['latitude', 'longitude', 'height'])
Latitude = namedtuple('Latitude', ['lat1', 'lat2', 'dlat'])
Longitude = namedtuple('Longitude', ['lon1', 'lon2', 'dlon'])
Height = namedtuple('Height', ['hgt1', 'hgt2', 'dhgt'])

Map = namedtuple('Map', ['epoch', 'height', 'data'])
MapGridDef = namedtuple('MapGridDef', ['lat', 'lon1', 'lon2', 'dlon', 'h'])


class NullContext:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class IonexV1:
    # заголовки, которые нужно считать и соответствующие им атрибуты класса
    header_label = {
        'EXPONENT': 'exponent',
        'MAP DIMENSION': 'dimension',
        'LAT1 / LAT2 / DLAT': 'latitude',
        'LON1 / LON2 / DLON': 'longitude',
        'HGT1 / HGT2 / DHGT': 'height',
    }

    # "Non-available TEC values are written as '9999'" (описание IONEX)
    none_value = 9999

    def __init__(self, file):
        self._exponent = -1
        self._dimension = None

        self._lat = None
        self._lon = None
        self._height = None

        self._tec_maps_numbers = []

        if isinstance(file, str):
            self._context_manager = open(file)
        else:
            self._context_manager = NullContext(file)

    @property
    def exponent(self):
        return self._exponent

    @exponent.setter
    def exponent(self, value):
        self._exponent = int(value[0:6])

    @property
    def dimension(self):
        return self._dimension

    @dimension.setter
    def dimension(self, value):
        self._dimension = int(value[0:6])

    @property
    def latitude(self):
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = Latitude(
            float(value[2:8]),
            float(value[8:14]),
            float(value[14:20]),
        )

    @property
    def longitude(self):
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = Longitude(
            float(value[2:8]),
            float(value[8:14]),
            float(value[14:20]),
        )

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = Height(
            float(value[2:8]),
            float(value[8:14]),
            float(value[14:20]),
        )

    @property
    def grid(self):
        return Grid(self._lat, self._lon, self._height)

    @staticmethod
    def _get_label(line):
        return line[60:].rstrip()

    def _read_header(self, file_object):
        label = ''
        while label != 'END OF HEADER':
            try:
                line = next(file_object)
            except StopIteration:
                raise IONEXUnexpectedEnd(file_object)

            label = self._get_label(line)
            if label not in self.header_label:
                continue
            setattr(self, self.header_label[label], line)

    @staticmethod
    def _parse_epoch(epoch_str):
        epoch_elements = []
        for i in range(0, 36, 6):
            v = int(epoch_str[i:i + 6])
            epoch_elements.append(v)
        epoch = datetime(*epoch_elements[0:4])

        # иногда минуты/секунды == 60, просто прибавляем как дельту
        epoch += timedelta(seconds=epoch_elements[4] * 60 + epoch_elements[5])
        return epoch

    @staticmethod
    def _parse_map_grid_def(def_str):
        grid_def = []
        for i in range(2, 30, 6):
            v = float(def_str[i:i + 6])
            grid_def.append(v)
        return MapGridDef(*grid_def)

    @staticmethod
    def _read_slice(line):
        return [int(v) for v in line.split()]

    def _read_map(self, file_object):
        """
        :return: ``namedtuple``, Map('Map', ['epoch', 'height', 'data'])
        """
        epoch = 'EPOCH OF CURRENT MAP'
        grid = 'LAT/LON1/LON2/DLON/H'

        # FIXME: сразу после начала карты может быть EXPONENT
        #        объединить с header_label (?)
        parser = {
            epoch: self._parse_epoch,
            grid: self._parse_map_grid_def,
        }

        metadata = {
            epoch: None,
            grid: None,
        }

        data = []
        while True:
            try:
                line = next(file_object)
            except StopIteration:
                raise IONEXUnexpectedEnd(file_object)

            label = self._get_label(line)
            if label in parser:
                metadata[label] = parser[label](line)
                continue
            # TODO: проверять номер карты (?)
            elif label == 'END OF TEC MAP':
                break
            data += self._read_slice(line)

        return Map(
            epoch=metadata[epoch],
            # XXX: всегда будет заключительное значение высоты
            height=metadata[grid][4],
            data=data,
        )

    def _next_map(self):
        with self._context_manager as file_object:
            self._read_header(file_object)

            while True:
                try:
                    line = next(file_object).rstrip()
                except StopIteration:
                    filename = getattr(file_object, 'name', '<Unknown>')
                    warnings.warn(
                        'Unexpected end of the file {}.'.format(filename)
                    )
                    break

                label = self._get_label(line)
                if label == 'START OF TEC MAP':
                    self._tec_maps_numbers.append(int(line[:6]))
                    epoch, height, map_data = self._read_map(file_object)
                    yield IonexMap(
                        exponent=self.exponent,
                        epoch=epoch,
                        longitude=self.longitude,
                        latitude=self.latitude,
                        height=self.height,
                        tec=map_data,
                        none_value=self.none_value,
                    )
                    continue

                if label == 'END OF FILE':
                    break

    def __iter__(self):
        return self._next_map()
