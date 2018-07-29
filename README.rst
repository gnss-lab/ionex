=====
ionex
=====

Модуль для чтения карт в формате IONEX.


*************
Использование
*************

Коротко
-------

::

    import ionex

    with open('igsg0010.00i') as file:
        inx = ionex.reader(file)
        for ionex_map in inx:
            print(ionex_map.epoch)
            print(ionex_map.tec)


Содержание модуля
------------------


~~~~~~~~~~~~~~~~~~~~
`ionex.reader(file)`
~~~~~~~~~~~~~~~~~~~~

Возвращает читалку файла в формате IONEX. Читалка - итерируемый объект, который
на каждой итерации возвращает экземпляр `IonexMap` очередной карты, прочитанной
из файла.

**Параметры**

- `file`: `str` | `file`, путь к файлу IONEX или объект файла.

**Исключения**

- `IONEXError`, неизвестный тип или версия переданного файла.
- `IONEXUnexpectedEnd`, неполный файл.
- `IONEXMapError`, ошибки при обработке карты.


~~~~~~~~~~~~~~~~~~~~~~
`class ionex.IonexMap`
~~~~~~~~~~~~~~~~~~~~~~

Класс карты IONEX, содержит карту значений ПЭС и мета-данные.

**Атрибуты**


- `grid`: `namedtuple`, определение сетки для карты, содержит два `namedtupla`:

    - `grid.latittude` = `namedtuple('Latitude', ['lat1', 'lat2', 'dlat'])`
      определение сетки по широте от `lat1` до `lat2` с шагом `dlat`;

    - `grid.longitude` = `namedtuple('Longitude', ['lon1', 'lon2', 'dlon'])`
      определение сетки по долготе от `lon1` до `lon2` с шагом `dlon`.

- `tec`: `list`, данные ПЭС; одномерный список, представляет собой
  набор широтных "срезов" со значениями ПЭС.

  Начало каждого среза соответствует широте `grid.latitude.lat1`, конец --
  `grid.latitude.lat2`, с шагом, равным `grid.latitude.dlat`.

  Долгота первого среза соответствует `grid.longitude.lon1`, долгота
  последнего -- `grid.longitude.lon2`, с шагом, равным `grid.longitude.dlon`.

- `height`: `float`, высота, с которой ассоциированы данные карты.

- `epoch`: `datetime`, дата и время карты ПЭС.

*********
Установка
*********

Сейчас лучше устанавливать в editable-mode::

    $ pip install -e git+https://github.com/gnss-lab/ionex.git#egg=ionex


******
Ошибки
******

Ошибки стоит оформлять на `issues <https://github.com/gnss-lab/ionex/issues>`_.

Как оформить ошибку:

- опишите, как её можно воспроизвести;
- приложите файлы IONEX, при обработке которых возникла
  ошибка или укажите ссылку на эти файлы.

********
Лицензия
********

Distributed under the terms of the
`MIT <https://github.com/gnss-lab/gnss-tec/blob/master/LICENSE.txt>`_
license, gnss-tec is free and open source software.

Copyright Ilya Zhivetiev, 2018.
