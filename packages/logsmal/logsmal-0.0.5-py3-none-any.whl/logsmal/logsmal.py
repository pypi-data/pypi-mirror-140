from enum import Enum
from typing import Final
from typing import Optional, Any, Callable, Union

from .independent.helpful import toBitSize
from .independent.log_file import LogFile
from .independent.zip_file import ZippFile, ZipCompression

class MetaLogger:
    """
    Мета данные логгера
    """
    #: Конец цвета
    reset_: Final[str] = "\x1b[0m"
    blue: Final[str] = "\x1b[96m"
    yellow: Final[str] = "\x1b[93m"
    read: Final[str] = "\x1b[91m"
    green: Final[str] = "\x1b[92m"
    #: Серый
    gray: Final[str] = "\x1b[90m"
    #: Неон
    neon: Final[str] = "\x1b[96m"


class CompressionLog(Enum):
    """
    Варианты действий при достижении лимита размера файла
    """
    #: Перезаписать файл (Удалить все и начать с 0)
    rewrite_file = lambda _path_file: CompressionLog._rewrite_file(_path_file)

    #: Сжать лог файл в архив, а после удалить лог файл
    zip_file = lambda _path_file: CompressionLog._zip_file(_path_file)

    @staticmethod
    def _rewrite_file(_path_file: str):
        _f = LogFile(_path_file)
        logger.system_info(f"{_path_file}:{_f.sizeFile()}", flag="DELETE")
        _f.deleteFile()

    @staticmethod
    def _zip_file(_path_file: str):
        ZippFile(f"{_path_file}.zip").writeFile(_path_file, compression=ZipCompression.ZIP_LZMA)
        LogFile(_path_file).deleteFile()
        logger.system_info(_path_file, flag="ZIP_AND_DELETE")


class loglevel:
    """
    Создание логгера
    """
    __slots__ = [
        "level",
        "fileout",
        "console_out",
        "color_flag",
        "color_loglevel",
        "max_size_file",
        "compression",
        "_cont_write_log_file",
    ]

    #: Через сколько записей в лог файл, проверять его размер.
    CONT_CHECK_SIZE_LOG_FILE = 10

    def __init__(
            self, level: str,
            fileout: Optional[str] = None,
            console_out: bool = True,
            color_flag: str = "",
            color_loglevel: str = "",
            max_size_file: Optional[Union[int, str]] = "10mb",
            compression: Optional[Union[CompressionLog, Callable]] = None,
    ):
        """
        Создать логгер

        :param level: Уровень
        :param fileout: Куда записать данные
        :param console_out: Нужно ли выводить данные в ``stdout``
        :param max_size_file: Максимальный размер(байтах), файла после которого происходит ``compression``.

        Также можно указать:

        - kb - Например 10kb
        - mb - Например 1mb
        - None - Без ограничений

        :param compression: Что делать с файлам после достижение ``max_size_file``
        """
        self.level: str = level
        self.fileout: Optional[str] = fileout
        self.console_out: bool = console_out
        self.color_flag: str = color_flag
        self.color_loglevel: str = color_loglevel
        self.max_size_file: Optional[int] = toBitSize(max_size_file) if max_size_file else None
        self.compression: Callable = compression if compression else CompressionLog.rewrite_file

        #: Сколько раз было записей в лог файл, до выполнения
        #: условия ``self._cont_write_log_file < CONT_CHECK_SIZE_LOG_FILE``
        self._cont_write_log_file = 0

    def __call__(self, data: str, flag: str = ""):
        """
        Вызвать логгер

        :param data:
        :param flag:
        :return:
        """
        self._base(data, flag)

    def _base(self, data: Any, flag: str):
        """
        Логика работы логера

        :param data:
        :param flag:
        :return:
        """
        if self.fileout:
            log_formatted = "{level}[{flag}]:{data}\n".format(
                level=self.level,
                flag=flag,
                data=data,
            )
            _f = LogFile(self.fileout)
            _f.appendFile(log_formatted)
            # Проверить размер файла
            self._check_size_log_file(_f)

        if self.console_out:
            log_formatted = "{color_loglevel}{level}{reset}{color_flag}[{flag}]{reset}:".format(
                level=self.level,
                color_loglevel=self.color_loglevel,
                reset=MetaLogger.reset_,
                flag=flag,
                color_flag=self.color_flag
            )
            print(f"{log_formatted}{data}")

    def _check_size_log_file(self, _file: LogFile):
        """
        Проверить размер файла при достижении условия определенного
        количества записи в файл

        :param _file: Файл
        """
        if self._cont_write_log_file > self.CONT_CHECK_SIZE_LOG_FILE or self._cont_write_log_file == 0:
            self._check_compression_log_file(size_file=_file.sizeFile())
        self._cont_write_log_file += 1

    def _check_compression_log_file(self, size_file: int):
        """
        Проверить нужно ли выполнять  ``compression``

        :param size_file: Размер файла в байтах
        """
        if self.max_size_file is not None:
            if size_file > self.max_size_file:
                self.compression(self.fileout)


class logger:
    """
    Стандартные логгеры
    """

    info = loglevel(
        "[INFO]",
        color_loglevel=MetaLogger.blue,
        color_flag=MetaLogger.yellow,
    )
    error = loglevel(
        "[ERROR]",
        color_loglevel=MetaLogger.read,
        color_flag=MetaLogger.yellow,
    )
    success = loglevel(
        "[SUCCESS]",
        color_loglevel=MetaLogger.green,
        color_flag=MetaLogger.gray,
    )

    #: Логгер для системных задач
    system_info: Final[loglevel] = loglevel(
        "[SYSTEM]",
        color_loglevel=MetaLogger.gray,
        color_flag=MetaLogger.gray,
        console_out=True
    )
    #: Логгер для системных задач
    system_error: Final[loglevel] = loglevel(
        "[SYSTEM]",
        color_loglevel=MetaLogger.gray,
        color_flag=MetaLogger.read,
        console_out=True
    )
