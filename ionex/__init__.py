from .ionex_file import IonexV1, NullContext
from .exceptions import IONEXError
from .exceptions import IONEXUnexpectedEnd

__all__ = ['reader']


def _get_version_type(line):
    return float(line[:8]), line[20]


def reader(file):
    """Возвращает читалку файла в формате IONEX.
    Читалка - итерируемый объект, на каждой итерации возвращает экземпляр
    ``ionex_map.IonexMap`` очередной карты, прочитанной из файла.

    :type file: str | file-object
    :param file: Путь к файлу IONEX или объект файла.

    :raises IONEXError:
        Если неизвестный тип или версия переданного файла.

    :raises IONEXUnexpectedEnd:
        Неполный файл.

    :raises IONEXMapError:
        Если возникли ошибки при обработке карты.
    """
    readers = {
        1.0: IonexV1,
    }

    if isinstance(file, str):
        context_manager = open(file)
    else:
        context_manager = NullContext(file)

    with context_manager as file_object:
        try:
            file_ver, file_type = _get_version_type(next(file_object))
        except StopIteration:
            raise IONEXUnexpectedEnd(file_object)

        if file_type != 'I':
            raise IONEXError('Unknown file type.')
        if file_ver not in readers:
            raise IONEXError('Unsupported version: {}'.format(file_ver))

        reader_class = readers[file_ver]
        return reader_class(file)
