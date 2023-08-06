# -*- coding: utf-8 -*-

from .__info__ import __version__, __description__

try:
    from brainpp_yl.fs import compat_mode

    compat_mode()
except ModuleNotFoundError:
    pass
