"""Tests fuer das Basisprojekt (Raumschiff, PowerUp, Asteroid, Weltraumwelt)."""

from __future__ import annotations

import pytest


from pyfoot import EAST, NORTH, SOUTH, WEST
from ships import NormalSpaceship
from space import (
    Asteroid,
    PopupMessage,
    PowerUp,
    RandomAsteroid,
    RandomPowerUp,
    SensorSpaceship,
    Spaceship,
    SpaceshipError,
    SpaceWorld,
)


class ProbeShip(Spaceship):
    """Ein Raumschiff ohne eigene Anweisungen, fuer Einzeltests."""

    def init(self) -> None:
        pass


class ProbeSensorShip(SensorSpaceship):
    """Ein Sensorschiff ohne eigene Anweisungen, fuer Einzeltests."""

    def init(self) -> None:
        pass


def _world_with_ship(
    ship: Spaceship, x: int = 2, y: int = 2, width: int = 8, height: int = 8
) -> SpaceWorld:
    world = SpaceWorld(width, height)
    world.add_object(ship, x, y)
    return world


# ----------------------------------------------------------------------
# Weltraumwelt
# ----------------------------------------------------------------------


def test_space_world_has_default_size() -> None:
    world = SpaceWorld()
    assert (world.width, world.height) == (8, 8)
    assert world.cell_size == SpaceWorld.CELL_SIZE


def test_alert_appears_and_can_be_cleared() -> None:
    world = SpaceWorld(6, 6)
    world.alert("Achtung")
    assert len(world.objects(PopupMessage)) == 1

    world.clear_alerts()
    assert world.objects(PopupMessage) == []


def test_second_alert_replaces_the_first() -> None:
    world = SpaceWorld(6, 6)
    world.alert("Erster")
    world.alert("Zweiter")
    assert len(world.objects(PopupMessage)) == 1


# ----------------------------------------------------------------------
# Fliegen
# ----------------------------------------------------------------------


def test_move_changes_position() -> None:
    ship = ProbeShip()
    _world_with_ship(ship)
    ship.move()
    assert (ship.x, ship.y) == (3, 2)


def test_move_several_cells_at_once() -> None:
    ship = ProbeShip()
    _world_with_ship(ship, 1, 1)
    ship.move(3)
    assert (ship.x, ship.y) == (4, 1)


def test_turn_left_goes_counter_clockwise() -> None:
    ship = ProbeShip()
    _world_with_ship(ship)

    assert ship.rotation == EAST
    ship.turn_left()
    assert ship.rotation == NORTH
    ship.turn_left()
    assert ship.rotation == WEST
    ship.turn_left()
    assert ship.rotation == SOUTH
    ship.turn_left()
    assert ship.rotation == EAST


def test_leaving_the_world_is_prevented() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship, 7, 2)

    with pytest.raises(SpaceshipError, match="endet die Welt"):
        ship.move()

    # Position unveraendert und Hinweis sichtbar
    assert (ship.x, ship.y) == (7, 2)
    assert len(world.objects(PopupMessage)) == 1


def test_flying_into_an_asteroid_is_prevented() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship, 2, 2)
    world.add_object(Asteroid(), 3, 2)

    with pytest.raises(SpaceshipError, match="Asteroid"):
        ship.move()

    assert (ship.x, ship.y) == (2, 2)


def test_multi_step_move_stops_in_front_of_obstacle() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship, 1, 1)
    world.add_object(Asteroid(), 4, 1)

    with pytest.raises(SpaceshipError):
        ship.move(5)

    # Die ersten beiden Felder waren frei, das dritte nicht.
    assert (ship.x, ship.y) == (3, 1)


# ----------------------------------------------------------------------
# PowerUps
# ----------------------------------------------------------------------


def test_initial_power_up_supply() -> None:
    assert ProbeShip().power_up_count == Spaceship.DEFAULT_POWER_UPS
    assert ProbeShip(power_ups=7).power_up_count == 7


def test_negative_supply_is_rejected() -> None:
    with pytest.raises(ValueError):
        ProbeShip(power_ups=-1)


def test_drop_and_collect_power_up() -> None:
    ship = ProbeShip(power_ups=3)
    world = _world_with_ship(ship)

    ship.drop_power_up()
    assert ship.power_up_count == 2
    assert len(world.objects_at(2, 2, PowerUp)) == 1

    ship.collect_power_up()
    assert ship.power_up_count == 3
    assert world.objects_at(2, 2, PowerUp) == []


def test_collecting_without_power_up_raises() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship)

    with pytest.raises(SpaceshipError, match="PowerUp"):
        ship.collect_power_up()

    assert len(world.objects(PopupMessage)) == 1


def test_dropping_without_supply_raises() -> None:
    ship = ProbeShip(power_ups=0)
    _world_with_ship(ship)

    with pytest.raises(SpaceshipError, match="keines mehr"):
        ship.drop_power_up()


def test_say_shows_text_above_the_ship() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship, 2, 2)
    ship.say("Hallo")
    assert world.text_at(2, 1) is not None


def test_say_at_top_edge_moves_text_below() -> None:
    ship = ProbeShip()
    world = _world_with_ship(ship, 2, 0)
    ship.say(42)
    assert world.text_at(2, 1) is not None


# ----------------------------------------------------------------------
# Sensorik
# ----------------------------------------------------------------------


def test_detect_power_up_on_own_cell() -> None:
    ship = ProbeSensorShip()
    world = _world_with_ship(ship)

    assert ship.is_power_up_here() is False
    world.add_object(PowerUp(), 2, 2)
    assert ship.is_power_up_here() is True


def test_detect_free_cell_ahead() -> None:
    ship = ProbeSensorShip()
    world = _world_with_ship(ship, 2, 2)

    assert ship.can_move() is True

    world.add_object(Asteroid(), 3, 2)
    assert ship.can_move() is False


def test_world_edge_counts_as_blocked() -> None:
    ship = ProbeSensorShip()
    _world_with_ship(ship, 7, 2)
    assert ship.can_move() is False


def test_query_facing_directions() -> None:
    ship = ProbeSensorShip()
    _world_with_ship(ship)

    assert ship.is_facing_east() is True
    ship.turn_left()
    assert ship.is_facing_north() is True
    ship.turn_left()
    assert ship.is_facing_west() is True
    ship.turn_left()
    assert ship.is_facing_south() is True


def test_asteroid_sensors_are_missing_on_purpose() -> None:
    """Diese Methoden zu schreiben ist eine Schueleraufgabe (M0 Abschnitt 1.4)."""
    assert not hasattr(ProbeSensorShip(), "is_asteroid_left")
    assert not hasattr(ProbeSensorShip(), "is_asteroid_right")


def test_turn_right_is_missing_on_purpose() -> None:
    """turn_right() aus drei turn_left() zu bauen ist die Methoden-Einstiegsaufgabe."""
    assert not hasattr(ProbeShip(), "turn_right")


# ----------------------------------------------------------------------
# Zufallsobjekte
# ----------------------------------------------------------------------


def test_random_power_up_stays_at_probability_one() -> None:
    world = SpaceWorld(4, 4)
    world.add_object(RandomPowerUp(1.0), 1, 1)
    assert len(world.objects(PowerUp)) == 1


def test_random_power_up_vanishes_at_probability_zero() -> None:
    world = SpaceWorld(4, 4)
    world.add_object(RandomPowerUp(0.0), 1, 1)
    assert world.objects(PowerUp) == []


def test_random_asteroid_stays_at_probability_one() -> None:
    world = SpaceWorld(4, 4)
    world.add_object(RandomAsteroid(1.0), 1, 1)
    assert len(world.objects(Asteroid)) == 1


def test_random_asteroid_vanishes_at_probability_zero() -> None:
    world = SpaceWorld(4, 4)
    world.add_object(RandomAsteroid(0.0), 1, 1)
    assert world.objects(Asteroid) == []


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_probability_is_rejected(value: float) -> None:
    with pytest.raises(ValueError):
        RandomPowerUp(value)
    with pytest.raises(ValueError):
        RandomAsteroid(value)


def test_random_power_up_is_roughly_half() -> None:
    world = SpaceWorld(4, 4)
    for _ in range(400):
        world.add_object(RandomPowerUp(0.5), 1, 1)
    count = len(world.objects(PowerUp))
    assert 150 < count < 250


# ----------------------------------------------------------------------
# Abnahmekriterium M2
# ----------------------------------------------------------------------


def test_example_from_normal_rabbit_runs_unchanged() -> None:
    """Die Anweisungsfolge aus NormalRabbit.init() als Python-Entsprechung.

    Java-Original:
        move(); putCarrot(); move(); turnLeft();
    """
    ship = NormalSpaceship()
    world = SpaceWorld(9, 9)
    world.add_object(ship, 0, 5)

    world._act_cycle()

    assert (ship.x, ship.y) == (2, 5)
    assert ship.rotation == NORTH
    assert ship.power_up_count == Spaceship.DEFAULT_POWER_UPS - 1
    assert len(world.objects_at(1, 5, PowerUp)) == 1
    assert ship.init_done is True
