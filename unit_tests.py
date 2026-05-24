import unittest
import os
import sys
import time

import numpy as np

import assets
import physics
import shapes


AIR = 0
SOLID = 1
SAND = 2


def make_grid(width=10, height=10, fill=AIR):
    """Create a small RGB-like grid cell array: material, object id, texture id."""
    return np.array([[(fill, 0, 0) for _ in range(width)] for _ in range(height)])


def make_benchmark_grid(width, height, grid_type, seed=0):
    """
    Build deterministic grids for timing comparisons.

    The benchmark uses several map styles because each implementation can behave
    differently depending on how many sand cells are allowed to move.
    """
    rng = np.random.default_rng(seed)
    grid = make_grid(width, height)

    if grid_type == "sparse_sand":
        sand_mask = rng.random((height, width)) < 0.15
        solid_mask = rng.random((height, width)) < 0.05
    elif grid_type == "mixed_obstacles":
        sand_mask = rng.random((height, width)) < 0.30
        solid_mask = rng.random((height, width)) < 0.20
    elif grid_type == "dense_sand":
        sand_mask = rng.random((height, width)) < 0.65
        solid_mask = rng.random((height, width)) < 0.10
    else:
        raise ValueError(f"Unknown grid type: {grid_type}")

    # SOLID is applied first, then SAND overwrites part of it. This keeps the
    # density definitions simple and deterministic for every benchmark run.
    grid[solid_mask] = (SOLID, 0, 0)
    grid[sand_mask] = (SAND, 8, 2)
    return grid


def benchmark_step_efficiency(
    sizes=(25, 50, 75, 100, 150, 200),
    grid_types=("sparse_sand", "mixed_obstacles", "dense_sand"),
    repeats=5,
    output_path="step_efficiency.png",
    show=False,
):
    """
    Compare physics.step and physics.step_vectorized on several grid sizes.

    The function saves a plot showing execution time as a function of map size.
    It is intentionally not a unittest because timing tests are noisy and should
    not make the regular automated test suite slower or flaky.
    """
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-worms-tests")
    import matplotlib.pyplot as plt

    timings = {
        grid_type: {"regular": [], "vectorized": []}
        for grid_type in grid_types
    }

    empty_player_1 = assets.Player()
    empty_player_2 = assets.Player()

    print("\nBenchmarking regular step vs vectorized step")
    print(f"Grid sizes: {sizes}")
    print(f"Repeats per case: {repeats}\n")

    for grid_type in grid_types:
        print(f"Grid type: {grid_type}")
        for size in sizes:
            grid = make_benchmark_grid(size, size, grid_type, seed=size)

            regular_runs = []
            vectorized_runs = []

            for _ in range(repeats):
                regular_grid = grid.copy()
                start = time.perf_counter()
                physics.step(regular_grid, empty_player_1, empty_player_2)
                regular_runs.append(time.perf_counter() - start)

                vectorized_grid = grid.copy()
                start = time.perf_counter()
                physics.step_vectorized(
                    vectorized_grid,
                    empty_player_1,
                    empty_player_2,
                    direction=1,
                )
                vectorized_runs.append(time.perf_counter() - start)

            regular_mean = float(np.mean(regular_runs))
            vectorized_mean = float(np.mean(vectorized_runs))
            timings[grid_type]["regular"].append(regular_mean)
            timings[grid_type]["vectorized"].append(vectorized_mean)

            print(
                f"  {size:>3}x{size:<3} | "
                f"regular={regular_mean:.6f}s | "
                f"vectorized={vectorized_mean:.6f}s"
            )

    fig, axes = plt.subplots(1, len(grid_types), figsize=(5 * len(grid_types), 4))
    if len(grid_types) == 1:
        axes = [axes]

    for axis, grid_type in zip(axes, grid_types):
        cell_counts = [size * size for size in sizes]
        axis.plot(cell_counts, timings[grid_type]["regular"], marker="o", label="regular step")
        axis.plot(
            cell_counts,
            timings[grid_type]["vectorized"],
            marker="o",
            label="vectorized step",
        )
        axis.set_title(grid_type.replace("_", " "))
        axis.set_xlabel("map size (number of cells)")
        axis.set_ylabel("time per step (seconds)")
        axis.grid(True, alpha=0.3)
        axis.legend()

    fig.suptitle("Physics step efficiency comparison")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\nSaved benchmark plot to {output_path}")

    if show:
        plt.show()

    return timings


class VerboseTestCase(unittest.TestCase):
    """Base class that prints compact progress messages during test execution."""

    def setUp(self):
        super().setUp()
        description = self.shortDescription() or self._testMethodName
        print(f"\n[TEST] {description}")

    def log_success(self, message):
        print(f"  [OK] {message}")


class TestWormMethods(VerboseTestCase):
    def test_take_damage(self):
        """Worm health decreases by exactly the incoming damage amount."""
        cases = [
            (3, 1, 2),
            (2.5, 0.75, 1.75),
        ]

        for initial_health, damage, expected_health in cases:
            with self.subTest(initial_health=initial_health, damage=damage):
                print(
                    f"  Checking damage: health={initial_health}, "
                    f"damage={damage}, expected={expected_health}"
                )
                worm = assets.Player.Worm(5, 5, health=initial_health)
                worm.take_damage(damage)
                self.assertEqual(worm.health, expected_health)
                self.log_success("worm health was updated correctly")

    def test_is_supposed_to_fall(self):
        """A worm should fall when there is air below or diagonally below it."""
        cases = [
            ("air directly below", (5, 4), True),
            ("solid below and diagonals", None, False),
        ]

        for name, air_cell, expected in cases:
            with self.subTest(name=name):
                print(f"  Checking fall detection: {name}")
                grid = make_grid()
                worm = assets.Player.Worm(5, 5)

                # Fill the three possible support cells before optionally
                # opening one of them for the current scenario.
                grid[4, 5] = (SOLID, 0, 0)
                grid[4, 4] = (SOLID, 0, 0)
                grid[4, 6] = (SOLID, 0, 0)

                if air_cell is not None:
                    x, y = air_cell
                    grid[y, x] = (AIR, 0, 0)

                self.assertIs(bool(worm.is_supposed_to_fall(grid)), expected)
                self.log_success(f"fall detection returned {expected}")

    def test_gravity(self):
        """Gravity moves the worm vertically first, then diagonally if needed."""
        cases = [
            ("falls vertically", None, (5, 4)),
            ("slides right", (6, 4), (6, 4)),
        ]

        for name, diagonal_air_cell, expected_position in cases:
            with self.subTest(name=name):
                print(f"  Checking gravity movement: {name}")
                grid = make_grid()
                worm = assets.Player.Worm(5, 5)

                # Start from a blocked position and open exactly the cell that
                # should be used by the gravity algorithm.
                grid[4, 5] = (SOLID, 0, 0)
                grid[4, 4] = (SOLID, 0, 0)
                grid[4, 6] = (SOLID, 0, 0)

                if diagonal_air_cell is None:
                    grid[4, 5] = (AIR, 0, 0)
                else:
                    x, y = diagonal_air_cell
                    grid[y, x] = (AIR, 0, 0)

                worm.gravity(grid)
                self.assertEqual((worm.x_pos, worm.y_pos), expected_position)
                self.log_success(f"worm moved to {expected_position}")


class TestWeaponMethods(VerboseTestCase):
    def test_missile_launch_trajectory(self):
        """Missile trajectories contain 50 points and end on the target."""
        cases = [
            ((0, 0, 10, 10), (0, 0)),
            ((5, 2, 5, 12), (5, 2)),
        ]

        missile = assets.Player.missile()

        for args, expected_end in cases:
            with self.subTest(args=args):
                print(f"  Checking missile trajectory with args={args}")
                x_target, y_target, x_pos, y_pos = args
                x_values, y_values = missile.launch_trajectory(
                    x_target, y_target, x_pos, y_pos
                )

                # The exact intermediate curve can change, but the sampled
                # length and endpoints define the public contract used by UI code.
                self.assertEqual(len(x_values), 50)
                self.assertEqual(len(y_values), 50)
                self.assertAlmostEqual(x_values[0], x_pos)
                self.assertAlmostEqual(y_values[0], y_pos)
                self.assertAlmostEqual(x_values[-1], expected_end[0])
                self.assertAlmostEqual(y_values[-1], expected_end[1])
                self.log_success("missile trajectory endpoints are correct")

    def test_strike_launch_trajectory(self):
        """Strike trajectories are vertical and contain 50 sampled points."""
        cases = [
            ((10, 20, 0, 0), 10),
            ((42, 3, 8, 9), 42),
        ]

        strike = assets.Player.strike()

        for args, expected_x in cases:
            with self.subTest(args=args):
                print(f"  Checking strike trajectory with args={args}")
                x_target, y_target, x_pos, y_pos = args
                x_values, y_values = strike.launch_trajectory(
                    x_target, y_target, x_pos, y_pos
                )

                self.assertEqual(len(x_values), 50)
                self.assertEqual(len(y_values), 50)
                self.assertTrue(np.all(x_values == expected_x))
                self.assertAlmostEqual(y_values[0], y_target + 108)
                self.assertAlmostEqual(y_values[-1], y_target)
                self.log_success("strike trajectory is vertical and reaches the target")


class TestGridMethods(VerboseTestCase):
    def test_rectangle_draw(self):
        """Rectangle.draw writes material, object id, and texture on the grid."""
        cases = [
            ((1, 2, 3, 2), 6),
            ((0, 0, 2, 4), 8),
        ]

        for args, expected_count in cases:
            with self.subTest(args=args):
                print(f"  Checking rectangle draw with args={args}")
                x0, y0, dx, dy = args
                grid = make_grid()
                rectangle = shapes.Rectangle(
                    x0, y0, dx, dy, object_id=7, material=SOLID, texture=4
                )

                rectangle.draw(grid)

                # Count the changed material cells and inspect the rectangle
                # slice to ensure metadata was written in the same area.
                self.assertEqual(np.count_nonzero(grid[:, :, 0] == SOLID), expected_count)
                self.assertTrue(np.all(grid[y0 : y0 + dy, x0 : x0 + dx, 1] == 7))
                self.assertTrue(np.all(grid[y0 : y0 + dy, x0 : x0 + dx, 2] == 4))
                self.log_success(f"rectangle wrote {expected_count} solid cells")

    def test_transform(self):
        """transform changes nearby material and clears object ids only for AIR."""
        cases = [
            (0, "destroys cells and clears object ids"),
            (SAND, "turns cells into sand and keeps object ids"),
        ]

        for material, name in cases:
            with self.subTest(name=name):
                print(f"  Checking transform behavior: {name}")
                grid = np.array(
                    [[(SOLID, 5, 1) for _ in range(shapes.Nx)] for _ in range(shapes.Ny)]
                )

                shapes.transform(grid, 10, 10, 2, material)

                self.assertEqual(grid[10, 10, 0], material)
                if material == AIR:
                    self.assertEqual(grid[10, 10, 1], 0)
                else:
                    self.assertEqual(grid[10, 10, 1], 5)
                self.log_success("transform updated material and object id as expected")


class TestPhysicsMethods(VerboseTestCase):
    def test_step_vectorized_sand(self):
        """step_vectorized moves sand down first, then diagonally when blocked."""
        cases = [
            ("falls down", (4, 5), 1, (4, 4)),
            ("slides left", (4, 5), -1, (3, 4)),
        ]

        for name, start_position, direction, expected_position in cases:
            with self.subTest(name=name):
                print(f"  Checking vectorized sand movement: {name}")
                grid = make_grid()
                start_x, start_y = start_position
                grid[start_y, start_x] = (SAND, 8, 2)

                if name == "falls down":
                    grid[start_y - 2, start_x + 1] = (SOLID, 0, 0)

                if direction is not None and name != "falls down":
                    grid[start_y - 1, start_x] = (SOLID, 0, 0)

                player1 = assets.Player()
                player2 = assets.Player()

                new_grid, moved = physics.step_vectorized(
                    grid, player1, player2, direction=direction
                )

                expected_x, expected_y = expected_position
                self.assertTrue(moved)
                self.assertEqual(new_grid[expected_y, expected_x, 0], SAND)
                self.assertEqual(new_grid[expected_y, expected_x, 1], 8)
                self.log_success(f"sand moved to {expected_position}")


if __name__ == "__main__":
    if "--benchmark" in sys.argv:
        sys.argv.remove("--benchmark")
        benchmark_step_efficiency()
    else:
        unittest.main(verbosity=2)
