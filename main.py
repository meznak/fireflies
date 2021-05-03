# Import standard modules.
import argparse
import configparser
import sys

# Import non-standard modules.
import pygame as pg
from pygame.locals import *

# Import local modules
from firefly import Firefly

# Read and apply config settings
config_file = configparser.ConfigParser()
config_file.read('config.ini')
Firefly.config(config_file['firefly'])
CONFIG = {
    'title': config_file.get('main', 'title'),
    'logo': config_file.get('main', 'logo'),
    'count': config_file.getint('main', 'count'),
    'geometry': config_file.get('main', 'geometry')
}


def update(dt, flies):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame.
    If you want to have constant apparent movement no matter your framerate,
    what you can do is something like

    x += v * dt

    and this will scale your velocity based on time. Extend as necessary."""

    # Go through events that are passed to the script by the window.
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit(0)
        elif event.type == KEYDOWN:
            mods = pg.key.get_mods()
            if event.key == pg.K_q:
                # quit
                pg.quit()
                sys.exit(0)
            elif event.key == pg.K_UP:
                # add flies
                if mods & pg.KMOD_SHIFT:
                    add_flies(flies, 100)
                else:
                    add_flies(flies, 10)
            elif event.key == pg.K_DOWN:
                # remove flies
                if mods & pg.KMOD_SHIFT:
                    flies.remove(flies.sprites()[:100])
                else:
                    flies.remove(flies.sprites()[:10])
            elif event.key == pg.K_1:
                for fly in flies:
                    fly.max_force /= 2
                print("max force {}".format(flies.sprites()[0].max_force))
            elif event.key == pg.K_2:
                for fly in flies:
                    fly.max_force *= 2
                print("max force {}".format(flies.sprites()[0].max_force))
            elif event.key == pg.K_3:
                for fly in flies:
                    fly.perception *= .8
                print("perception {}".format(flies.sprites()[0].perception))
            elif event.key == pg.K_4:
                for fly in flies:
                    fly.perception *= 1.2
                print("perception {}".format(flies.sprites()[0].perception))
            elif event.key == pg.K_5:
                for fly in flies:
                    fly.crowding *= 0.8
                print("crowding {}".format(flies.sprites()[0].crowding))
            elif event.key == pg.K_6:
                for fly in flies:
                    fly.crowding *= 1.2
                print("crowding {}".format(flies.sprites()[0].crowding))
            elif event.key == pg.K_d:
                # toggle debug
                for fly in flies:
                    fly.debug = not fly.debug
            elif event.key == pg.K_r:
                # reset
                num_flies = len(flies)
                flies.empty()
                add_flies(flies, num_flies)

    for b in flies:
        b.update(dt, flies)


def draw(screen, background, flies):
    """
    Draw things to the window. Called once per frame.
    """

    # Redraw screen here
    flies.clear(screen, background)
    dirty = flies.draw(screen)

    # Flip the display so that the things we drew actually show up.
    pg.display.update(dirty)


def main(args):
    # Initialise pg.
    pg.init()

    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

    # Set up the clock to maintain a relatively constant framerate.
    fps = 60.0
    fpsClock = pg.time.Clock()

    # Set up the window.
    logo = pg.image.load(CONFIG['logo'])
    pg.display.set_icon(logo)
    pg.display.set_caption(CONFIG['title'])
    window_width, window_height = [int(x) for x in args.geometry.split("x")]
    flags = DOUBLEBUF

    screen = pg.display.set_mode((window_width, window_height), flags)
    screen.set_alpha(None)
    background = pg.Surface(screen.get_size()).convert()
    background.fill(pg.Color('black'))

    flies = pg.sprite.RenderUpdates()

    add_flies(flies, args.num_flies)

    # Main game loop.
    dt = 1/fps  # dt is the time since last frame.

    # Loop forever!
    while True:
        update(dt, flies)
        draw(screen, background, flies)
        dt = fpsClock.tick(fps)


def add_flies(flies, num_flies):
    for _ in range(num_flies):
        flies.add(Firefly())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Emergent flocking.')
    parser.add_argument('--geometry', metavar='WxH', type=str,
                        default=CONFIG['geometry'],
                        help='geometry of window')
    parser.add_argument('--number', dest='num_flies',
                        default=CONFIG['count'],
                        help='number of flies to generate')
    args = parser.parse_args()

    main(args)
