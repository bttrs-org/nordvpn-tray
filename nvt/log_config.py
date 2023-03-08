import sys
import os
import logging
from .utils import is_dev, user_data_dir


def config():
    if is_dev():
        logging.basicConfig(format='%(asctime)s [%(name)s][%(levelname)s] - %(message)s',
                            level=logging.DEBUG,
                            stream=sys.stdout)
    else:
        logging.basicConfig(format='%(asctime)s [%(name)s][%(levelname)s] - %(message)s',
                            level=logging.WARNING,
                            filename=os.path.join(user_data_dir(), 'app.log'))
