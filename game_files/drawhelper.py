"""Module providing reusable functions helpful with drawing"""
import math
import pygame

import constants, game

LINE_WIDTH = constants.TILE_SIZE // 8


def draw_arc(x0, y0, start_angle, stop_angle,
             color=constants.WALL_COLOR):
    """Draws arc at given coordinates with given angles in pi rad"""
    x_compensation = LINE_WIDTH / 2 if start_angle in [0, 3/2] else 0
    y_compensation = LINE_WIDTH / 2 if stop_angle  in [0, 3/2] else 0
    pygame.draw.arc(game.Game.WINDOW, color,
                    (x0 * constants.TILE_SIZE + x_compensation,
                     y0 * constants.TILE_SIZE + y_compensation,
                     constants.TILE_SIZE, constants.TILE_SIZE),
                    start_angle * math.pi, stop_angle * math.pi, LINE_WIDTH)


def draw_line(x0, y0, x1, y1, color=constants.WALL_COLOR):
    """Draws line from given start coordinates to end coordinates"""
    pygame.draw.line(game.Game.WINDOW, color,
                     (x0 * constants.TILE_SIZE,
                      y0 * constants.TILE_SIZE),
                     (x1 * constants.TILE_SIZE,
                      y1 * constants.TILE_SIZE),
                     LINE_WIDTH)


def draw_rect(x0, y0, width, height=0, offset=0,
              color=constants.BACKGROUND_COLOR):
    """Draws rectangle at given coordinates of certain width and height

    When height is not passed - a square is drawn
    """

    if height == 0:
        height = width
    pygame.draw.rect(game.Game.WINDOW, color,
                     (x0 * constants.TILE_SIZE + offset,
                      y0 * constants.TILE_SIZE + offset,
                      width, height))


def get_image_at(x, y):
    """Returns image found in sprite sheet at given coordinates"""
    rectangle = pygame.Rect((
        x * (constants.SPRITE_SIZE + constants.SPRITE_SPACING * 2)
        + constants.SPRITE_SPACING,
        y * (constants.SPRITE_SIZE + constants.SPRITE_SPACING * 2)
        + constants.SPRITE_SPACING,
        constants.SPRITE_SIZE,
        constants.SPRITE_SIZE
    ))
    image = pygame.Surface(rectangle.size).convert()
    image.set_colorkey(constants.BACKGROUND_COLOR)
    image.blit(game.Game.SPRITE_SHEET, (0, 0), rectangle)
    return image


def draw_text(string):
    """Draw given text on screen in place suitable for text drawing"""
    font = pygame.font.SysFont(pygame.font.get_default_font(),
                               constants.SPRITE_SIZE)
    text = font.render(string, True, constants.TEXT_COLOR,
                       constants.BACKGROUND_COLOR)
    text_rect = text.get_rect()
    text_rect.center = (constants.GAMEMAP_WIDTH_PX // 2,
                        constants.GAMEMAP_HEIGHT_PX // 2 +
                        2 * constants.TILE_SIZE)
    game.Game.WINDOW.blit(text, text_rect)


def clear_text():
    """Clears drawn text"""
    draw_rect(constants.GAMEMAP_WIDTH // 2 - 5,
              constants.GAMEMAP_HEIGHT // 2 + 2,
              width=10 * constants.TILE_SIZE,
              height=constants.TILE_SIZE)
