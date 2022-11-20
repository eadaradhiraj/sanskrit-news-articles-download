import logging


class MyFormatter(logging.Formatter):
    def format(self, record):
        record.class_name = ""
        if record.args and type(record.args) is dict:
            record.class_name = record.args.get("class_name", "") + " : "
        return super().format(record)


logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setFormatter(
    MyFormatter(
        "[ %(levelname)s ] - %(message)s (%(class_name)s%(funcName)s() -> %(filename)s:%(lineno)s)"
    )
)

logging.basicConfig(handlers=[ch])
