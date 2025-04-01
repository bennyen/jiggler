import os
import platform
import logging
import time
from random import randint
from threading import Thread, current_thread
from time import sleep

import click
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.mouse import Controller as MouseController

from src import state

log = logging.getLogger(__name__)

keyboard = KeyboardController()
mouse = MouseController()
keyboardListener = KeyboardListener(on_press=state.update_jiggle_time, on_release=state.update_jiggle_time)
mouseListener = MouseListener(
    on_move=state.update_jiggle_time,
    on_click=state.update_jiggle_time,
    on_scroll=state.update_jiggle_time)
special_keys = {
    "Darwin": "cmd",
    "Linux": "alt",
    "Windows": "alt",
}

def key_press():
    keyboard.press(Key.shift)
    keyboard.release(Key.shift)
    log.debug(f"[keypress]\tPressed {Key.shift} key")


def switch_screen(tabs, key):
    modifier = getattr(Key, key)
    with keyboard.pressed(modifier):
        t = tabs if tabs else randint(1, 3)

        for _ in range(t):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        log.debug(f"[switch_screen]\tSwitched tab {t} {modifier} {Key.tab}")


def move_mouse(pixels):
    mouse.move(pixels, pixels)
    x, y = list("{:.2f}".format(coord) for coord in mouse.position)
    log.debug(f"[move_mouse]\tMoved mouse to {x}, {y}")


def jiggle(pixels, mode, tabs, key):
    c = mode[randint(0,len(mode)-1)]
    if c == "m":
        move_mouse(pixels)
    if c == "k":
        key_press()
    if c == "s":
        switch_screen(tabs, key)
        

def _jiggle(pixels, mode, tabs, key):
    this = current_thread()
    this.alive = True
    while this.alive:
        if state.is_jiggle_time():
            jiggle(pixels, mode, tabs, key)
        else:
            sleep(0.1)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-s",
    "--seconds",
    type=int,
    help="Seconds to wait between actions. Default is 10",
    default=10,
)
@click.option(
    "-p",
    "--pixels",
    type=int,
    help="Number of pixels the mouse should move. Default is 1",
    default=1,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["m", "k", "mk", "ks", "ms", "mks"]),
    help="Available options: m, k, mk, ks, ms, mks; default is mks. "
    "This is the action that will be executed when the user is idle at the defined interval: "
    "m -> moves mouse defined number of pixels; "
    "k -> presses shift key on keyboard; "
    "s -> switches windows on screen; ",
    default="mks",
)
@click.option("-t", "--tabs", type=int, help="Number of window tabs to switch screens")
@click.option(
    "-k",
    "--key",
    type=click.Choice(["alt", "cmd"]),
    help="Special key for switching windows",
    default=special_keys[platform.system()],
)
def start(seconds, pixels, mode, tabs, key):
    logging.basicConfig(
        level=logging.NOTSET,
        format='%(asctime)s %(levelname)s %(thread)d %(threadName)s %(name)s %% %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    state.set_jiggle_delay(seconds)
    try:
        threads = []
        threads.append(keyboardListener)
        threads.append(mouseListener)
        threads.append(Thread(target=_jiggle, args=(pixels, mode, tabs, key)))
        for t in threads:
            t.start()

        for t in threads:
            t.join()
    except KeyboardInterrupt as e:
        log.debug("Exiting...")
        for t in threads:
            t.alive = False
        for t in threads:
            t.join()

        log.debug("So you don't need me anymore?")
        os._exit(1)
