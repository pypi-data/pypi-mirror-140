## Использование

```python
from logsmal import logger

logger.success("Программа запущена", flag="RUN")
```

Создать кастомный логгер. Посмотрите все доступные аргменты :meth:`logsmal.loglevel.__init__()`

```python
from logsmal import loglevel, logger, CompressionLog

logger.MyLogger = loglevel(
    level="[melogger]",
    fileout="./log/mylog.log",
    max_size_file="10kb",
    console_out=False,
    compression=CompressionLog.zip_file
)
```