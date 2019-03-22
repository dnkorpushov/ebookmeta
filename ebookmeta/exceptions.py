

class Error(Exception):

    def __init__(self, msg=''):
        Exception.__init__(self, msg)
        self.msg = msg

    def __repr__(self):
        ret = 'ebookmeta.{} {}'.format(self.__class__.__name__, self.msg)
        return ret.strip()

    __str__ = __repr__


class BadFormat(Error):
    pass


class WriteEpubException(Error):
    pass


class UnknownFormatException(Error):
    pass


class BadEpubVersionException(Error):
    pass
