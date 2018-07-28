class IONEXError(Exception):
    pass


class IONEXMapError(IONEXError):
    pass


class IONEXUnexpectedEnd(IONEXError):
    def __init__(self, file_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = getattr(file_object, 'name', '<Unknown>')

    def __str__(self):
        return 'Unexpected end of the file: {}'.format(self.filename)
