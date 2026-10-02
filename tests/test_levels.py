"""Tests fuer die vorbereiteten Startwelten."""

from __future__ import annotations

from helpers import world_with

from pyfoot import Actor
from ships import NormalSpaceship
from levels import (
    Level0,
    Level1PowerUpRow,
    Level1aPowerUpField,
    Level2AsteroidWall,
    Level2aRandomPowerUps,
    Level3cPowerUpStack,
    Level3dGiantPowerUpField,
    Level3eRandomPowerUpRow,
    Level3fRandomPowerUpField,
    Level3gGiantRandomPowerUpField,
)
from space import (
    Asteroid,
    PowerUp,
    SpaceWorld,
    Spaceship,
)


def test_level0_places_a_spaceship() -> None:
    world = Level0()
    ships = world.objects(Spaceship)
    assert len(ships) == 1
    assert (ships[0].x, ships[0].y) == (0, 5)
    assert (world.width, world.height) == (9, 9)


def test_only_level0_brings_its_own_spaceship() -> None:
    """Alle anderen Welten bleiben leer -- das Schiff setzt man selbst ein."""
    ships: list[Spaceship] = Level0().objects(Spaceship)
    assert len(ships) == 1
    assert isinstance(ships[0], NormalSpaceship)
    assert (ships[0].x, ships[0].y) == Level0.START

    assert Level1PowerUpRow().objects(Spaceship) == []
    assert Level3cPowerUpStack().objects(Spaceship) == []


def test_power_up_row_fills_the_top_row() -> None:
    world = Level1PowerUpRow()
    assert (world.width, world.height) == (20, 25)
    assert len(world.objects(PowerUp)) == 20
    assert all(p.y == 0 for p in world.objects(PowerUp))


def test_power_up_field_is_a_rectangle() -> None:
    world = Level1aPowerUpField()
    power_ups = world.objects(PowerUp)
    assert len(power_ups) == 12
    assert {p.x for p in power_ups} == {3, 4, 5, 6}
    assert {p.y for p in power_ups} == {3, 4, 5}


def test_asteroid_wall_has_a_gap_column() -> None:
    world = Level2AsteroidWall()
    asteroids = world.objects(Asteroid)
    # Sieben feste Asteroiden plus einer, der zufaellig da ist.
    assert 7 <= len(asteroids) <= 8
    assert all(a.x == 3 for a in asteroids)


def test_random_power_ups_are_at_most_two() -> None:
    world = Level2aRandomPowerUps()
    assert len(world.objects(PowerUp)) <= 2


def test_power_up_stack_sits_on_one_cell() -> None:
    world = Level3cPowerUpStack()
    power_ups = world.objects(PowerUp)
    assert len(power_ups) > 0
    assert all((p.x, p.y) == (2, 2) for p in power_ups)


def test_giant_field_fills_every_cell() -> None:
    world = Level3dGiantPowerUpField()
    assert (world.width, world.height) == (25, 25)
    assert len(world.objects(PowerUp)) == 25 * 25


def test_random_row_stays_in_the_top_row() -> None:
    world = Level3eRandomPowerUpRow()
    assert all(p.y == 0 for p in world.objects(PowerUp))


def test_mixed_field_has_a_full_row_and_an_asteroid_row() -> None:
    world = Level3fRandomPowerUpField()
    assert len([p for p in world.objects(PowerUp) if p.y == 5]) == world.width
    assert len([a for a in world.objects(Asteroid) if a.y == 6]) == world.width


def test_giant_random_field_is_roughly_half_filled() -> None:
    world = Level3gGiantRandomPowerUpField()
    count = len(world.objects(PowerUp))
    assert 200 < count < 1000


def test_every_level_is_a_space_world() -> None:
    levels: list[SpaceWorld] = [
        Level0(),
        Level1PowerUpRow(),
        Level1aPowerUpField(),
        Level2AsteroidWall(),
        Level2aRandomPowerUps(),
        Level3cPowerUpStack(),
        Level3fRandomPowerUpField(),
    ]
    for world in levels:
        assert isinstance(world, SpaceWorld)
        assert world.cell_size == SpaceWorld.CELL_SIZE
        for actor in world.objects(Actor):
            assert world.contains(actor.x, actor.y)


def test_levels_place_their_ship_at_the_start_cell() -> None:
    world = world_with(Level1PowerUpRow, NormalSpaceship)
    ship = world.objects(NormalSpaceship)[0]
    assert (ship.x, ship.y) == (0, 0)
    assert world.objects(Spaceship) == [ship]
