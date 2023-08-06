#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan.at.hust.edu.cn
# @DATE: 2021-09-03 15:33:56
# @DESCRIPTION:

import logging
from pathlib import Path

current_path = Path(__file__).parent


class Logger(object):
    def __init__(self, logfile: Path = current_path / "../../test/tmp_result/evatools.log"):
        self.logfile = logfile

    def log(self, message) -> None:
        logger = logging.getLogger("EVAtool-subprocess")
        logger.setLevel(logging.INFO)
        logger.info(message)
