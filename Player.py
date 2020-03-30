import pygame
import enum
import Character

WALL = ' '


class Direction(enum.IntEnum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


class Player(Character.Character):
    def __init__(self, game, tile_x, tile_y):
        super().__init__(game)
        self.SPRITE_SHEET_ROW = 0
        self.ANIMATION_FRAME_COUNT = 3
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.x = (tile_x + 1) * self.game.map.tile_size
        self.y = (tile_y + 0.5) * self.game.map.tile_size
        self.speed = self.get_speed()

    def eat(self):
        pass

    def move(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.speed = self.get_speed()
                if event.key == pygame.K_LEFT:
                    self.next_direction = Direction.LEFT
                if event.key == pygame.K_RIGHT:
                    self.next_direction = Direction.RIGHT
                if event.key == pygame.K_UP:
                    self.next_direction = Direction.UP
                if event.key == pygame.K_DOWN:
                    self.next_direction = Direction.DOWN

        if 0 < self.x < self.game.map.get_width():
            if abs((self.x % self.game.map.tile_size) - self.game.map.tile_size / 2) <= self.speed / 2:
                if abs((self.y % self.game.map.tile_size) - self.game.map.tile_size / 2) <= self.speed / 2:
                    tile_x = self.x // self.game.map.tile_size
                    tile_y = self.y // self.game.map.tile_size

                    if self.direction != self.next_direction:
                        if self.next_direction == Direction.RIGHT and self.game.map.get_tile(tile_x + 1, tile_y) != WALL or \
                                self.next_direction == Direction.LEFT and self.game.map.get_tile(tile_x - 1, tile_y) != WALL or \
                                self.next_direction == Direction.UP and self.game.map.get_tile(tile_x, tile_y - 1) != WALL or \
                                self.next_direction == Direction.DOWN and self.game.map.get_tile(tile_x, tile_y + 1) != WALL:
                            self.x = (tile_x + 0.5) * self.game.map.tile_size
                            self.y = (tile_y + 0.5) * self.game.map.tile_size
                            self.direction = self.next_direction

                    if self.direction == Direction.RIGHT and self.game.map.get_tile(tile_x + 1, tile_y) == WALL or \
                            self.direction == Direction.LEFT and self.game.map.get_tile(tile_x - 1, tile_y) == WALL or \
                            self.direction == Direction.UP and self.game.map.get_tile(tile_x, tile_y - 1) == WALL or \
                            self.direction == Direction.DOWN and self.game.map.get_tile(tile_x, tile_y + 1) == WALL:
                        self.speed = 0

        if self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.UP:
            self.y -= self.speed

        if self.x <= -1 * self.game.map.tile_size / 2:
            self.x = self.game.map.get_width() + self.game.map.tile_size / 2
        elif self.x >= self.game.map.get_width() + self.game.map.tile_size / 2:
            self.x = -1 * self.game.map.tile_size / 2

    def draw(self):
        sprite_size = self.game.sprite_sheet.sprite_size
        frame = self.game.tick // 5 % 4
        if frame == 3:
            frame = 2
        self.game.window.blit(
            pygame.transform.rotate(
                self.game.sprite_sheet.get_image_at(frame, 0),
                90 * self.direction),
            (self.x - sprite_size / 2, self.y - sprite_size / 2))

    def get_speed(self):
        return self.game.map.tile_size / 6 * 0.8
