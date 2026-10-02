"""Die Welten des Kurses -- und deine eigenen.

Jede Welt liegt in einer eigenen Datei. **Sie gehoeren dir:** Du darfst
sie umbauen, und die Oberflaeche legt neue Welten ebenfalls hier ab.

Die gemeinsame Grundlage `StartWorld` steht dagegen in `space/` -- sie
gehoert zum vorgegebenen Teil.
"""

from __future__ import annotations

from .level0 import Level0
from .level1_power_up_row import Level1PowerUpRow
from .level1a_power_up_field import Level1aPowerUpField
from .level2_asteroid_wall import Level2AsteroidWall
from .level2a_random_power_ups import Level2aRandomPowerUps
from .level3c_power_up_stack import Level3cPowerUpStack
from .level3d_giant_power_up_field import Level3dGiantPowerUpField
from .level3e_random_power_up_row import Level3eRandomPowerUpRow
from .level3f_random_power_up_field import Level3fRandomPowerUpField
from .level3g_giant_random_power_up_field import Level3gGiantRandomPowerUpField
from .level4_logic_corridor import Level4LogicCorridor
from .level4a_power_up_street import Level4aPowerUpStreet
from .level4b_binary_number import Level4bBinaryNumber
from .level4c_tunnel import Level4cTunnel
from .level4d_tunnel import Level4dTunnel
from .level5_power_up_stack_row import Level5PowerUpStackRow
from .level6_for_loop import Level6ForLoop
from .level7_grid import Level7Grid

__all__ = [
    "Level0",
    "Level1PowerUpRow",
    "Level1aPowerUpField",
    "Level2AsteroidWall",
    "Level2aRandomPowerUps",
    "Level3cPowerUpStack",
    "Level3dGiantPowerUpField",
    "Level3eRandomPowerUpRow",
    "Level3fRandomPowerUpField",
    "Level3gGiantRandomPowerUpField",
    "Level4LogicCorridor",
    "Level4aPowerUpStreet",
    "Level4bBinaryNumber",
    "Level4cTunnel",
    "Level4dTunnel",
    "Level5PowerUpStackRow",
    "Level6ForLoop",
    "Level7Grid",
]
