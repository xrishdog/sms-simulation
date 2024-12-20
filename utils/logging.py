import logging
import sys

def configure_logger(logger):
    logger.setLevel(logging.DEBUG)  # Set the desired logging level here

    # Create a console handler that logs to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # Create a formatter with a timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
