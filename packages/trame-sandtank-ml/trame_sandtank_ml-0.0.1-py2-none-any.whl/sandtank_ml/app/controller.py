r"""
Bind methods to the trame controller
"""

from trame import controller as ctrl
from .engine import api


def bind_methods():
    ctrl.on_ready = api.initialize
    ctrl.parflow_run = api.run_parflow
    ctrl.ai_run = api.run_ai
    ctrl.xai_run = api.run_xai


def on_start():
    bind_methods()


def on_reload(reload_modules):
    # reload_modules(engine)
    bind_methods()
