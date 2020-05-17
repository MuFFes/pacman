import Character
import constants
import random
import math


class Ghost(Character.Character):
    def __init__(self, game, tile_x, tile_y, image_row):
        super().__init__(game, tile_x, tile_y)
        self.image_row = image_row
        self.direction = constants.Direction.RIGHT
        self.freeze = True
        self.in_base = True
        self.dead = False
        self.speed = constants.BASE_SPEED * 0.75
        self.home_corner = (0, 0)
        self.target = (0, 0)
        self.pellets_to_leave = 0
        self.state = constants.GhostState.SCATTER

    def get_chase_target(self):
        pass

    def update_target(self):
        if self.dead:
            self.target = self.game.barrier.get_entrance()
        elif self.state == constants.GhostState.CHASE:
            self.target = self.get_chase_target()
        elif self.state == constants.GhostState.SCATTER:
            self.target = self.home_corner

    def reverse_direction(self):
        if not self.dead:
            if self.direction == constants.Direction.RIGHT:
                self.direction = constants.Direction.LEFT
            elif self.direction == constants.Direction.LEFT:
                self.direction = constants.Direction.RIGHT
            elif self.direction == constants.Direction.DOWN:
                self.direction = constants.Direction.UP
            elif self.direction == constants.Direction.UP:
                self.direction = constants.Direction.DOWN

    def change_state(self, new_state):
        if not (self.state == constants.GhostState.FRIGHTENED and new_state == constants.GhostState.SCATTER or
                self.state == constants.GhostState.FRIGHTENED and new_state == constants.GhostState.CHASE):
            if not self.in_base:
                self.reverse_direction()
        self.state = new_state

    def get_possible_directions(self):
        possible_directions = []  # up, left, down, right - tiebreaker
        if self.game.map.get_tile(self.get_tile_x(), self.get_tile_y() - 1) != constants.WALL and \
                (self.dead or self.game.map.get_tile(self.get_tile_x(), self.get_tile_y())
                 not in [constants.INTERSECTION, constants.INTERSECTION2]) and \
                self.direction != constants.Direction.DOWN:
            possible_directions.append(
                (constants.Direction.UP, self.get_distance_to_target(self.get_tile_x(), self.get_tile_y() - 1)))
        if self.game.map.get_tile(self.get_tile_x() - 1, self.get_tile_y()) != constants.WALL and \
                self.direction != constants.Direction.RIGHT:
            possible_directions.append(
                (constants.Direction.LEFT, self.get_distance_to_target(self.get_tile_x() - 1, self.get_tile_y())))
        if self.game.map.get_tile(self.get_tile_x(), self.get_tile_y() + 1) != constants.WALL and \
                self.game.map.get_tile(self.get_tile_x(), self.get_tile_y() + 1) != constants.BARRIER and \
                self.direction != constants.Direction.UP:
            possible_directions.append(
                (constants.Direction.DOWN, self.get_distance_to_target(self.get_tile_x(), self.get_tile_y() + 1)))
        if self.game.map.get_tile(self.get_tile_x() + 1, self.get_tile_y()) != constants.WALL and \
                self.direction != constants.Direction.LEFT:
            possible_directions.append(
                (constants.Direction.RIGHT, self.get_distance_to_target(self.get_tile_x() + 1, self.get_tile_y())))
        return possible_directions

    def get_distance_to_target(self, x, y):
        return ((x - self.target[0]) ** 2 + (y - self.target[1]) ** 2) ** (1 / 2)

    def move(self):
        if not self.freeze:
            if self.in_base:
                self.target = self.game.barrier.get_entrance()
                if abs(self.x - self.target[0] * constants.TILE_SIZE - constants.TILE_SIZE / 2) <= self.speed / 2:
                    if abs(self.y - self.target[1] * constants.TILE_SIZE - constants.TILE_SIZE / 2) <= self.speed / 2:
                        self.in_base = False
                        self.target = self.home_corner
                        self.direction = constants.Direction.LEFT
                        self.game.barrier.visible = True
                    else:
                        self.x = self.target[0] * constants.TILE_SIZE + constants.TILE_SIZE / 2
                        self.direction = constants.Direction.UP
            else:
                if 0 < self.x < self.game.map.get_width():
                    if abs((self.y % constants.TILE_SIZE) - constants.TILE_SIZE / 2) <= self.speed / 2:
                        if abs((self.x % constants.TILE_SIZE) - constants.TILE_SIZE / 2) <= self.speed / 2:
                            self.update_target()
                            possible_directions = self.get_possible_directions()
                            if len(possible_directions) >= 2 or \
                                    (len(possible_directions) == 1 and possible_directions[0] != self.direction):
                                self.x = (self.get_tile_x() + 0.5) * constants.TILE_SIZE
                                self.y = (self.get_tile_y() + 0.5) * constants.TILE_SIZE
                                if self.state == constants.GhostState.FRIGHTENED and not self.dead:
                                    self.direction = sorted(possible_directions, key=lambda x: random.random())[0][0]
                                else:
                                    self.direction = sorted(possible_directions, key=lambda x: x[1])[0][0]
                        if self.dead and abs((self.x + self.speed / 2) % constants.TILE_SIZE) <= self.speed:
                            sign = math.copysign(1, (self.x % constants.TILE_SIZE - constants.TILE_SIZE / 2))
                            if self.game.barrier.get_entrance() == (self.get_tile_x() + sign * 0.5, self.get_tile_y()):
                                self.direction = constants.Direction.DOWN
                            if self.game.barrier.get_spawn() == (self.get_tile_x() + sign * 0.5, self.get_tile_y()):
                                self.dead = False
                                self.in_base = True
                                self.state = self.game.previous_ghosts_state

            self.update_speed()
            if self.direction == constants.Direction.RIGHT:
                self.x += self.speed
            elif self.direction == constants.Direction.LEFT:
                self.x -= self.speed
            elif self.direction == constants.Direction.DOWN:
                self.y += self.speed
            elif self.direction == constants.Direction.UP:
                self.y -= self.speed

            if self.x <= -1 * constants.TILE_SIZE / 2:
                self.x = self.game.map.get_width() + constants.TILE_SIZE / 2
            elif self.x >= self.game.map.get_width() + constants.TILE_SIZE / 2:
                self.x = -1 * constants.TILE_SIZE / 2
        else:
            self.unfreeze()

    def unfreeze(self):
        pellets = sum(1 for i in self.game.map.get_pellets())
        if pellets <= self.game.map.total_pellets - self.pellets_to_leave:
            self.game.barrier.visible = False
            self.freeze = False

    def draw(self):
        sprite_size = constants.SPRITE_SHEET_SPRITE_SIZE
        if not self.freeze:
            frame = int(self.game.tick * constants.ANIMATION_SPEED) % 2
        else:
            frame = 0

        if self.dead:
            self.game.window.blit(
                self.game.sprite_sheet.get_image_at(4 + self.direction, 5),
                (self.x - sprite_size / 2, self.y - sprite_size / 2))
        elif self.state == constants.GhostState.FRIGHTENED:
            if self.game.player.fright <= 100:
                frame += int(self.game.tick * constants.ANIMATION_SPEED / 2) % 2 * 2
            self.game.window.blit(
                self.game.sprite_sheet.get_image_at(frame, 5),
                (self.x - sprite_size / 2, self.y - sprite_size / 2))
        else:
            self.game.window.blit(
                self.game.sprite_sheet.get_image_at(frame + self.direction * 2, self.image_row),
                (self.x - sprite_size / 2, self.y - sprite_size / 2))

    def update_speed(self):
        if not self.dead and self.state == constants.GhostState.FRIGHTENED:
            fright_multiplier = constants.get_level_based_constant(self.game.level, constants.GHOST_SPEED_MULTIPLIER)[1]
            self.speed = constants.BASE_SPEED * fright_multiplier
        else:
            multiplier = constants.get_level_based_constant(self.game.level, constants.GHOST_SPEED_MULTIPLIER)[0]
            self.speed = constants.BASE_SPEED * multiplier
