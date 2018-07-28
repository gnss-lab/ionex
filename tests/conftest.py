import os
from io import StringIO
from contextlib import contextmanager

import pytest

TEST_DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_data',
)


@contextmanager
def get_file_object(filename):
    file_object = None
    try:
        file_path = os.path.join(TEST_DATA_DIR, filename)
        file_object = open(file_path)
        yield file_object
    finally:
        if file_object is not None:
            file_object.close()


@pytest.fixture
def ionex_file_object():
    with get_file_object('ionex_file.00i') as file_object:
        yield file_object


@pytest.fixture(params=['filename', 'fileobject'])
def ionex_file(request):
    if request.param == 'filename':
        return os.path.join(TEST_DATA_DIR, 'ionex_file.00i')

    if request.param == 'fileobject':
        return request.getfixturevalue('ionex_file_object')


@pytest.fixture
def ionex_file_no_end_of_file():
    with get_file_object('ionex_file.00i') as file_object:
        content = file_object.readlines()
    content.pop(-1)
    file_object = StringIO(''.join(content))
    return file_object


@pytest.fixture
def one_map_file():
    file_obj = None
    try:
        file_path = os.path.join(TEST_DATA_DIR, 'one_map.xxi')
        file_obj = open(file_path)
        yield file_obj
    finally:
        if file_obj is not None:
            file_obj.close()


@pytest.fixture
def one_map_file_data():
    file_path = os.path.join(TEST_DATA_DIR, 'one_map_data.txt')
    with open(file_path) as file_obj:
        contents = file_obj.read()
    data = eval(contents)
    return data
