import asyncio
import multiprocessing
from functools import partial
from concurrent.futures import ProcessPoolExecutor

from trame import state, async_utils

from .parflow.run import parflow_run
from .ai.run import ai_run
from .xai.run import xai_run

MULTI_PROCESS_MANAGER = None
PROCESS_EXECUTOR = None


def initialize(**kwargs):
    global MULTI_PROCESS_MANAGER, PROCESS_EXECUTOR
    MULTI_PROCESS_MANAGER = multiprocessing.Manager()
    SPAWN = multiprocessing.get_context("spawn")
    PROCESS_EXECUTOR = ProcessPoolExecutor(1, mp_context=SPAWN)

    # Do a first run to fill parflow viz
    run_parflow()


# -----------------------------------------------------------------------------
# Parflow execution
# -----------------------------------------------------------------------------


def run_parflow():
    exec_parflow(left=state.pf_bc_left, right=state.pf_bc_right)


def exec_parflow(left=25, right=25, time=10):
    loop = asyncio.get_event_loop()
    queue = MULTI_PROCESS_MANAGER.Queue()

    async_utils.decorate_task(
        loop.run_in_executor(
            PROCESS_EXECUTOR,
            partial(parflow_run, queue, left, right, time),
        )
    )
    async_utils.create_state_queue_monitor_task(queue)


# -----------------------------------------------------------------------------
# AI execution
# -----------------------------------------------------------------------------


async def run_ai():
    with state.monitor():
        state.ai_running = True

    await asyncio.sleep(0.1)

    with state.monitor():
        state.ai = ai_run(state.pf_bc_left, state.pf_bc_right)
        state.ai_running = False


# -----------------------------------------------------------------------------
# XAI execution
# -----------------------------------------------------------------------------


async def run_xai():
    with state.monitor():
        state.xai_running = True

    await asyncio.sleep(0.1)

    with state.monitor():
        state.xai = await xai_run()
        state.xai_running = False
