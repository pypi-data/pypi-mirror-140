import logging


class LoggingAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):

        metadata = self.extra

        service = kwargs.pop("servico", metadata.get("servico"))
        module = kwargs.pop("modulo", metadata.get("modulo"))
        event_status = kwargs.pop(
            "evento_status", metadata.get("evento_status")
        )
        tag_event = kwargs.pop("tag_evento", metadata.get("tag_evento"))

        log = f"{service} {module} {event_status} {tag_event} {msg}"

        return log, kwargs


def adapt_logger(
    logger: logging.Logger, kwargs, formatter: logging.Formatter = None
):

    syslog = logging.StreamHandler()

    if not formatter:
        formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(message)s"
        )

    syslog.setFormatter(formatter)
    logger.addHandler(syslog)
    logger.propagate = False
    adapter = LoggingAdapter(logger, kwargs)

    return adapter
