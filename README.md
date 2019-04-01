# Legend-of-Lanea

A Zeldaesque adventure for the Pokitto

## Creating your own world

WARNING: The map format is subject to change in later versions

### World

A world (WorldData) is composed of maps (MapData) organised in a cartesian grid. Going out of a map automatically load the next map. For example if the player is in map at 1,1 and he goes outside of the map on the right side, the game will load the map at 2,1. If the player goes outside of the world bounds, or if there is no map set at the location, the player won and the game is finished.

Here is a small example about creating a 3x3 world with 4 maps:

```
import data_type as dt

world = dt.World(3, 3)
world.starting_map = map_1_2
world.set_map_at(1, 2, map_1_2)
world.set_map_at(1, 1, map_1_1)
world.set_map_at(0, 1, map_0_1)
world.set_map_at(0, 0, map_0_0)
```

### Map

Maps are 32x32 tilemaps edited as sprite. The meaning of each pixel is the following:

* 0x0 player
* 0x1 entity 1
* 0x2 entity 2
* 0x3 cliff
* 0x4 stalk
* 0x5 tree
* 0x6 custom_ground
* 0x7 wall
* 0x8 water
* 0x9 ground
* 0xA custom_solid
* 0xB grass
* 0xC entity 3
* 0xD entity 4
* 0xE entity_5
* 0xF entity_6

custom_ground, custom_solid, wall and entity 1-6 are configurable for each map. Here is a short example:

```
map_demoPixels = b'<32x32 sprite data>'
map_0_0 = dt.MapData(map_dungeonPixels)
map_0_0.entity_3 = dt.ENTITY_SLIME
map_0_0.entity_3_tid = dt.TILE_GROUND
map_0_0.custom_ground = gfx.tile_carpet
map_0_0.custom_solid = gfx.tile_statue
map_0_0.tile_wall = gfx.wall_dungeon
```

Note that for each entity, underlying tile (tid) must be set.

# Text

Each test sequence is represented by a Python list. Each string element is a narrative text. Each list (inside the list) element is a text said by Lanea. Lanea can either say single line or two lines sentences.

```
['"Danger!"', '"Slimes ahead!"', ['That\'s reassuring.']]
```

```
['"Village of Roadshow"', ['Maybe they', 'serve beer?']]
```
