class InvalidLogLevel(Exception):

    def __init__(self, error, levels):

        super().__init__('Wrong log level {0}, must be one of the following: {1}'.format(error, levels))


class PermissionDenied(Exception):

    def __init__(self, path):

        super().__init__('Permission denied to create file {0}, in specified path'.format(path))
