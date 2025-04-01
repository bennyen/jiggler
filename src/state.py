import time
import logging

log = logging.getLogger(__name__)


class State:
    def __init__(self):
        self.running = True
        self.paused = True
        self.last_jiggle_time = 0
        self.jiggle_delay = 10

state = State()

def set_jiggle_delay(delay):
    state.jiggle_delay = delay


def is_jiggle_time():
    return time.time() - state.last_jiggle_time >= state.jiggle_delay


def update_jiggle_time():
    state.last_jiggle_time = time.time()
    log.debug(f"updated jiggle time to: {state.last_jiggle_time}")

def is_running():
    return state.running


def is_running_sync():
    while __is_paused() and is_running():
        time.sleep(0.1)

    return is_running()


def stop():
    if state.running:
        state.running = False
        log.debug('stopping')


def __is_paused():
    return state.paused


def pause():
    if not state.paused:
        state.paused = True
        log.debug('paused')
        kb.release_keys()
        time.sleep(30)


def unpause():
    if state.paused:
        state.paused = False
        log.debug('unpaused')
