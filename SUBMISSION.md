# HW6 submission

## AI-use declaration

I used ChatGPT to help me understand the homework instructions and some Python concepts. It also helped me write and check parts of the code, fix errors, and prepare the report. I completed the handwritten calculations for Part A by myself. I also ran the code and checked the results myself.

## Setup and reproduction

**Environment:**
- Python: 3.13.15
- Gymnasium: 1.4.0
- Operating system: Windows
- Development environment: Visual Studio Code

**Installation commands:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "gymnasium[toy-text]"
```

If PowerShell restricts script execution, the virtual environment can be activated after running:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the virtual environment again.

**Run Part B:**

```powershell
python part_b.py
```

The program saves the experiment results and episode traces in `outputs/`.

## Part A — Paper calculations

The handwritten calculations were completed and committed to GitHub before coding.

**Scanned pages:**

[Part A — handwritten calculations](part_a/)

The pages contain:

- V1 values for every nonterminal tile.
- The three requested V2 calculations.
- Best actions and arrows.
- Explanations of the reward and transition rules.

The discount factor was γ = 0.9. Terminal states have value 0, and rewards are received when entering destination tiles.

The requested V2 values were:

| State | V2 | Best action |
|---|---:|---|
| Mud (1,2) | 8.00 | Right |
| (1,3) | 10.00 | Right |
| Ice (2,3) | 5.21 | Up |

## Part B — FrozenLake

### Fixed policy, written before the experiments

The fixed policy was defined before running the experiments.

The FrozenLake environment uses the standard 4×4 map:

```text
SFFF
FHFH
FFFH
HFFG
```

Actions are represented as:

- 0 = Left
- 1 = Down
- 2 = Right
- 3 = Up

The fixed policy assigns the following actions to nonterminal states:

| State | Action |
| ----- | ------ |
| 0     | Down   |
| 1     | Right  |
| 2     | Down   |
| 3     | Left   |
| 4     | Down   |
| 6     | Down   |
| 8     | Right  |
| 9     | Right  |
| 10    | Down   |
| 13    | Right  |
| 14    | Right  |

Terminal states 5, 7, 11, 12, and 15 do not require actions.

The fixed policy was designed to follow a safe path in the non-slippery environment:

0 → 4 → 8 → 9 → 10 → 14 → 15

This route reaches the goal in six steps without entering any holes.

### Results

Each condition was tested with three batch seeds (11, 22, 33), with 50 episodes per batch.

| Slippery? | Policy | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Success % | Mean steps |
| --------- | ------ | ---------: | --------: | --------: | --------------: | --------: | ---------: |
| No        | Random |         11 |         0 |        50 |               0 |        0% |       8.14 |
| No        | Random |         22 |         1 |        49 |               0 |        2% |       7.56 |
| No        | Random |         33 |         0 |        50 |               0 |        0% |       6.88 |
| No        | Fixed  |         11 |        50 |         0 |               0 |      100% |       6.00 |
| No        | Fixed  |         22 |        50 |         0 |               0 |      100% |       6.00 |
| No        | Fixed  |         33 |        50 |         0 |               0 |      100% |       6.00 |
| Yes       | Random |         11 |         0 |        50 |               0 |        0% |       8.06 |
| Yes       | Random |         22 |         0 |        50 |               0 |        0% |       7.60 |
| Yes       | Random |         33 |         0 |        50 |               0 |        0% |       7.98 |
| Yes       | Fixed  |         11 |         3 |        47 |               0 |        6% |       4.52 |
| Yes       | Fixed  |         22 |         2 |        48 |               0 |        4% |       5.06 |
| Yes       | Fixed  |         33 |         0 |        50 |               0 |        0% |       4.06 |

**Output files:**

- [All episode results](outputs/part_b_episodes.csv)
- [Summary statistics](outputs/part_b_summary.csv)
- [Successful episode trace](outputs/part_b_success_trace.txt)
- [Failed episode trace](outputs/part_b_failed_trace.txt)

**Explanation:**

The fixed policy achieved 100% success without slipping because the agent always moved in the intended direction and followed the planned safe route.

With slipping enabled, the agent could move in a different direction from the selected action. This increased the risk of entering holes and reduced the fixed policy's success rate.

The results varied between batches because different seeds produced different random action sequences and stochastic transitions.

In this experiment, the robot did not learn anything. The random policy simply chose random directions, while the fixed policy followed the same rules in every episode. Neither policy changed during the experiments.

## Part C — Custom solver

### Compare code with paper

I implemented Value Iteration using the exact map and transition rules from Part A, with a discount factor of 0.9.

The computed V1 values were:

```text
-1  -1  10   0
-1   #  -1   0
-1  -1  -1  -1
```

The three requested V2 values were:

| Cell | Handwritten V2 | Python V2 |
|---|---:|---:|
| Mud (1,2) | 8.00 | 8.00 |
| (1,3) | 10.00 | 10.00 |
| Ice (2,3) | 5.21 | 5.21 |

All computed values matched my handwritten calculations. There were no discrepancies.

### Values, policies and convergence

**Original map**

- Converged: True
- Iterations: 12
- Final value change: 2.1652931048166124e-07

Value map:

```text
4.200  8.000  10.000  0.000
2.780    #     5.824  0.000
1.536  2.818   4.242  2.818
```

Policy map:

```text
→ → → G
↑ # ↑ H
→ → ↑ ←
```

Saved file: [Original value and policy maps](outputs/part_c_original_maps.txt)

**Extended map**

The extended map adds sand (D, reward -2) and shallow water (W, reward -5).

- Converged: True
- Iterations: 11
- Final value change: 2.405881232014906e-07

Value map:

```text
4.200  8.000  10.000  0.000
2.780    #     5.824  0.000
1.502  2.818   4.242  2.818
```

Policy map:

```text
→ → → G
↑ # ↑ H
↑ → ↑ ←
```

Saved file: [Extended value and policy maps](outputs/part_c_extended_maps.txt)

The convergence tolerance was 0.000001, with a maximum of 10,000 iterations.

For equal action values, the tie-breaking order was Up, Down, Left, Right.

### Simulation results

Each map was tested using three batches of 50 episodes, with batch seeds 11, 22 and 33. The maximum episode length was 100 steps.

| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |
|---|---|---:|---:|---:|---:|---:|
| Original | 11 | 42 | 8 | 0 | 4.98 | 0.891 |
| Original | 22 | 46 | 4 | 0 | 5.04 | 1.915 |
| Original | 33 | 48 | 2 | 0 | 5.04 | 2.492 |
| Extended | 11 | 50 | 0 | 0 | 5.00 | 1.502 |
| Extended | 22 | 50 | 0 | 0 | 5.00 | 1.502 |
| Extended | 33 | 50 | 0 | 0 | 5.00 | 1.502 |

The complete results are saved in:

- [Episode results](outputs/part_c_episodes.csv)
- [Simulation summary](outputs/part_c_summary.csv)

### Explain your results

Adding sand and shallow water changed the optimal action at the starting cell from Right to Up. The starting value decreased from 1.536 to 1.502.

In the original map, the robot follows a path through the ice tile. Since movement from ice is stochastic, there is a risk of falling into the hole. In 150 simulations, 136 episodes reached the goal and 14 ended in the hole.

In the extended map, the robot avoids the ice tile and follows a deterministic route. All 150 episodes reached the goal. However, the route has additional floor costs, resulting in a slightly lower starting value.

The computed values represent expected discounted returns over an infinite horizon. The simulation results are averages from a limited number of episodes with a 100-step limit, so they may differ from the theoretical values.

### Rule checks

I tested the environment rules before trusting the solver.

| Check | Result |
|---|---|
| Boundary movement | PASS |
| Wall collision | PASS |
| Ice probabilities sum to 1.0 | PASS |
| Mud entry reward = -3 | PASS |
| Sand entry reward = -2 | PASS |
| Water entry reward = -5 | PASS |
| No transitions or rewards after Goal | PASS |
| No transitions or rewards after Hole | PASS |

All eight checks passed.

The results are saved in [Environment checks](outputs/part_c_checks.txt).

The solver and simulations can be reproduced using:

```bash
python part_c.py
```