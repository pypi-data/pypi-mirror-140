#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import MagicMock as _MagicMock


class MagicMock(_MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if name is not None:
        #     self.name = name
