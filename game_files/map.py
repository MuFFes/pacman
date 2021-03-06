"""Module containing immutable map class and methods to access its elements"""
import re
from dataclasses import dataclass

import constants

NEIGHBOR_COORDINATES = [
    (-1, -1), (0, -1), (+1, -1),
    (-1,  0),          (+1,  0),
    (-1, +1), (0, +1), (+1, +1),
]

WALL_RULES = [re.compile(x) for x in """
    ^(...11.10)|(.0..1.10)|(.1.01.10)|(.0.01.1.)$
    ^(.0.10.1.)|(.0.1101.)|(.1.1.01.)$
    ^(.1.10.0.)|(01.11...)|(0..10.1.)$
    ^(.1.01.0.)|(.10.1.1.)$
    ^(.1.0..1.)|(.1..0.1.)$
    ^........$
""".split()]


@dataclass
class Tile:
    """Dataclass needed for map tiles representation"""
    x: float
    y: float
    cell: str


class Map:
    """Class containing tiles (read from file) and methods to access them"""
    def __init__(self, map_file):
        with open(map_file) as file:
            self.game_map = [line.rstrip('\n') for line in file]
        self.tiles = []
        for y, line_str in enumerate(self.game_map):
            for x, cell in enumerate(line_str):
                self.tiles.append(Tile(x, y, cell))
        self.total_pellets = sum(1 for i in self.get_pellets())

    def get_tile(self, x, y):
        """Returns type of tile at given coordinates"""
        if x < 0 or x > self.tiles[-1].x:
            return False
        if y < 0 or y > self.tiles[-1].y:
            return False
        return next(t for t in self.tiles if t.x == x and t.y == y).cell

    def get_coordinates(self, cell):
        """Returns coordinates of first tile of given cell type"""
        tile = next(t for t in self.tiles if t.cell == cell)
        return tile.x, tile.y

    def get_pellets(self):
        """Returns generator of all pellet tiles in the map"""
        for tile in self.tiles:
            if tile.cell in [constants.PELLET,
                             constants.PELLET2,
                             constants.POWER_PELLET]:
                yield tile

    def get_barriers(self):
        """Returns generator of all barrier tiles in the map"""
        for tile in self.tiles:
            if tile.cell == constants.BARRIER:
                yield tile.x, tile.y

    def get_walls(self):
        """Returns generator of all walls in the map"""
        for tile in [t for t in self.tiles if t.cell == constants.WALL]:
            pattern_string = ""
            for dx, dy in NEIGHBOR_COORDINATES:
                if self.get_tile(dx + tile.x, dy + tile.y) == constants.WALL:
                    pattern_string += "1"
                else:
                    pattern_string += "0"

            for wall_type, regex in enumerate(WALL_RULES):
                if regex.match(pattern_string):
                    yield tile.x, tile.y, wall_type
                    break
