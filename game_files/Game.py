# pylint: disable=bad-whitespace,no-member,too-many-function-args
import pygame
import time
import random
import os

from game_files import Player, constants, Ghosts, Map, Barrier, drawhelper

os.environ['SDL_VIDEO_WINDOW_POS'] = "512, 32"


class Game:
    window = pygame.display.set_mode((
        constants.GAMEMAP_WIDTH * constants.TILE_SIZE,
        constants.GAMEMAP_HEIGHT * constants.TILE_SIZE
    ))
    sprite_sheet = pygame.image.load(constants.SPRITE_SHEET).convert()

    def __init__(self):
        self.map = Map.Map()
        self.tick = 0
        self.level = 0
        self.score = 0
        self.barrier = None
        self.player = None
        self.fruit = 0
        self.lives = 4
        self.combo = 1
        self.wait = 0
        self.ghosts = {}
        self.previous_ghosts_state = constants.SCATTER

    def initialize_level(self, next_level):
        player_x, player_y = self.map.get_coordinates('s')
        blinky_x, blinky_y = self.map.get_coordinates('b')
        pinky_x,  pinky_y  = self.map.get_coordinates('p')
        inky_x,   inky_y   = self.map.get_coordinates('i')
        clyde_x,  clyde_y  = self.map.get_coordinates('c')
        self.player = Player.Player(self, player_x, player_y)
        self.ghosts = {
            "blinky": Ghosts.Blinky(self, blinky_x, blinky_y),
            "pinky": Ghosts.Pinky(self, pinky_x, pinky_y),
            "inky": Ghosts.Inky(self, inky_x, inky_y),
            "clyde": Ghosts.Clyde(self, clyde_x, clyde_y)
        }
        self.barrier = Barrier.Barrier(list(self.map.get_barriers()))
        self.combo = 1
        self.fruit = 0
        self.update_caption()
        self.wait = 1
        if next_level:
            self.map.initialize_map()
            self.draw_walls()
            self.draw_pellets()
            self.level += 1
            self.tick = 0
        else:
            self.lives -= 1
            if self.lives == 0:
                self.draw_text("GAME OVER!")
                pygame.display.update()
                while True:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            return

    def update_caption(self):
        pygame.display.set_caption("Pacman level: " + str(self.level) +
                                   " score: " + str(self.score) +
                                   " lives: " + str(self.lives))

    def draw_text(self, string):
        font = pygame.font.SysFont(pygame.font.get_default_font(), constants.SPRITE_SIZE)
        text = font.render(string, True, constants.TEXT_COLOR, constants.BACKGROUND_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (constants.GAMEMAP_WIDTH_PX // 2,
                            constants.GAMEMAP_HEIGHT_PX // 2 + 2 * constants.TILE_SIZE)
        self.window.blit(text, text_rect)

    def clear_text(self):
        drawhelper.draw_rect(constants.GAMEMAP_WIDTH // 2 - 5,
                             constants.GAMEMAP_HEIGHT // 2 + 2,
                             width=10 * constants.TILE_SIZE,
                             height=constants.TILE_SIZE)

    def step(self):
        start_time = time.time()
        if not self.wait:
            if self.player.eat():
                self.spawn_fruit()
                if self.next_level():
                    return (time.time() - start_time) * 1000
            else:
                self.player.move()
            self.change_ghost_states()
            if self.check_collisions():
                return (time.time() - start_time) * 1000
            for ghost in self.ghosts.values():
                ghost.move()
            self.draw_fruit()
            self.draw_pellets()
            self.draw_characters()
            pygame.display.update()  # room for improvement
            self.tick += 1
            self.clear_characters()
        else:
            self.clear_fruit()
            self.draw_pellets()
            self.draw_characters()
            self.draw_text("R E A D Y !")
            pygame.display.update()

            events = pygame.event.get()
            keys = [pygame.K_RIGHT, 0, pygame.K_LEFT, 0]
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in keys:
                        self.player.direction = keys.index(event.key)
                        self.player.next_direction = keys.index(event.key)
                    self.wait = 0
                    self.clear_characters()
                    self.clear_text()
        return (time.time() - start_time) * 1000

    def check_collisions(self):
        for ghost in self.ghosts.values():
            if not ghost.dead:
                if ghost.get_tile_x() == self.player.get_tile_x():
                    if ghost.get_tile_y() == self.player.get_tile_y():
                        if ghost.state == constants.FRIGHTENED:
                            self.score += 200 * self.combo
                            self.combo *= 2
                            self.update_caption()
                            ghost.dead = True
                            ghost.update_target()
                        else:
                            self.initialize_level(False)
                            return True
        return False

    def next_level(self):
        if sum(1 for i in self.map.get_pellets()) == 0:
            self.initialize_level(True)
            return True
        return False

    def change_ghost_states(self):
        if self.player.fright > 0:
            self.player.fright -= 1
        else:
            if any(g for g in self.ghosts.values() if g.state == constants.FRIGHTENED):
                for ghost in self.ghosts.values():
                    ghost.change_state(self.previous_ghosts_state)
            cycle_times = constants.get_level_based_constant(self.level, constants.GHOST_MODE_CYCLE)
            second = self.tick / constants.TICKRATE - \
                self.player.power_pellets * constants.get_level_based_constant(self.level, constants.FRIGHT_TIME)
            if second in cycle_times:
                cycle = cycle_times.index(second)
                new_state = constants.SCATTER if cycle % 2 else constants.CHASE
                self.previous_ghosts_state = new_state
                for ghost in self.ghosts.values():
                    ghost.change_state(new_state)

    def draw_walls(self):
        for wall_x, wall_y, wall_type in self.map.get_walls():
            {
                0: lambda x, y: drawhelper.draw_arc(x + .5, y + .5, 1/2,   1),
                1: lambda x, y: drawhelper.draw_arc(x - .5, y + .5,   0, 1/2),
                2: lambda x, y: drawhelper.draw_arc(x - .5, y - .5, 3/2,   0),
                3: lambda x, y: drawhelper.draw_arc(x + .5, y - .5,   1, 3/2),
                4: lambda x, y: drawhelper.draw_line(x + .5, y, x + .5, y + 1),
                5: lambda x, y: drawhelper.draw_line(x, y + .5, x + 1, y + .5),
            }[wall_type](wall_x, wall_y)
        pygame.display.update()

    def draw_characters(self):
        self.barrier.draw()
        self.player.draw()
        for ghost in self.ghosts.values():
            ghost.draw()

    def clear_characters(self):
        self.barrier.clear()
        self.player.clear()
        for ghost in self.ghosts.values():
            ghost.clear()

    def spawn_fruit(self):
        pellets = sum(1 for i in self.map.get_pellets())
        if self.map.total_pellets - pellets in constants.FRUIT_SPAWN:
            self.fruit = random.randint(
                9 * constants.TICKRATE, 10 * constants.TICKRATE)

    def draw_fruit(self):
        if self.fruit > 0:
            fruit_x, fruit_y = self.map.get_coordinates('f')
            fruit_image_col = constants.get_level_based_constant(
                self.level, constants.FRUITS)[0]
            offset = constants.TILE_SIZE / 2 - constants.SPRITE_SIZE / 2
            self.window.blit(
                self.get_image_at(fruit_image_col, constants.FRUIT_IMAGE_ROW),
                ((fruit_x + 0.5) * constants.TILE_SIZE + offset,
                 fruit_y * constants.TILE_SIZE + offset))
            self.fruit -= 1
            if self.fruit == 0:
                self.clear_fruit()

    def clear_fruit(self):
        fruit_x, fruit_y = self.map.get_coordinates('f')
        offset = (constants.TILE_SIZE - constants.SPRITE_SIZE) / 2
        if self.fruit == 0:
            drawhelper.draw_rect(fruit_x + 0.5, fruit_y, constants.SPRITE_SIZE,
                                 offset=offset)

    def draw_pellets(self):
        tile_size = constants.TILE_SIZE
        size = tile_size / 8
        offset = tile_size / 2 - size / 2

        for pellet_x, pellet_y, pellet_type in self.map.get_pellets():
            if pellet_type == '.':
                drawhelper.draw_rect(pellet_x, pellet_y, size,
                                     offset=offset,
                                     color=constants.PELLET_COLOR)
            elif pellet_type == 'o':
                pygame.draw.circle(self.window, constants.PELLET_COLOR,
                                   (int((pellet_x + 0.5) * tile_size),
                                    int((pellet_y + 0.5) * tile_size)),
                                   int(size * 2))

    def get_image_at(self, x, y):
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
        image.blit(self.sprite_sheet, (0, 0), rectangle)
        return image
