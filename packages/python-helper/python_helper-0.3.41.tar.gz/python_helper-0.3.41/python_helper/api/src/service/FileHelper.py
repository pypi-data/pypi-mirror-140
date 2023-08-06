from python_helper.api.src.domain import Constant as c
from python_helper.api.src.service import LogHelper


def getFileLines(filePath: str, encoding: str = c.UTF_8):
    lines = []
    try:
        with open(filePath, c.READ, encoding=encoding) as file :
            lines = file.readlines()
    except Exception as exception:
        LogHelper.error(getFileLines, 'Not possible to read lines', exception, muteStackTrace=True)
        raise exception
    return lines
