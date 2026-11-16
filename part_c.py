import random
import csv
import os

# Карта из Part A
original_map = [
    ".M.G",
    ".#IH",
    "S..."
]

# Расширенная карта с песком и водой
extended_map = [
    ".M.G",
    ".#IH",
    "SD.W"
]

# Награды за вход в каждую клетку
rewards = {
    ".": -1,
    "S": -1,
    "M": -3,
    "I": -1,
    "G": 10,
    "H": -10,
    "D": -2,
    "W": -5
}

# Основные параметры
gamma = 0.9
max_iterations = 10000
tolerance = 0.000001

# Возможные действия робота
actions = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1)
}

print("Original map:")
for row in original_map:
    print(row)

print("\nExtended map:")
for row in extended_map:
    print(row)


def move(grid, state, action):
    # Получаем текущую позицию
    row, col = state

    # Находим направление движения
    dr, dc = actions[action]
    new_row = row + dr
    new_col = col + dc

    # Проверяем границы карты
    if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
        return state

    # Проверяем стену
    if grid[new_row][new_col] == "#":
        return state

    return (new_row, new_col)


def get_transitions(grid, state, action):
    # Терминальные клетки не имеют дальнейших переходов
    row, col = state
    tile = grid[row][col]

    if tile in ["G", "H"]:
        return []

    # Вероятности движения на льду
    if tile == "I":
        if action in ["Up", "Down"]:
            directions = [
                (action, 0.8),
                ("Left", 0.1),
                ("Right", 0.1)
            ]
        else:
            directions = [
                (action, 0.8),
                ("Up", 0.1),
                ("Down", 0.1)
            ]
    else:
        # На остальных клетках движение точное
        directions = [(action, 1.0)]

    transitions = []

    for direction, probability in directions:
        next_state = move(grid, state, direction)

        # Награда зависит от клетки назначения
        next_row, next_col = next_state
        next_tile = grid[next_row][next_col]
        reward = rewards[next_tile]

        transitions.append((probability, next_state, reward))

    return transitions

def value_iteration_step(grid, values):
    # Создаём новую таблицу значений
    new_values = {}

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            state = (row, col)
            tile = grid[row][col]

            # Пропускаем стены
            if tile == "#":
                continue

            # Терминальные клетки имеют значение 0
            if tile in ["G", "H"]:
                new_values[state] = 0
                continue

            # Вычисляем значение каждого действия
            action_values = []

            for action in actions:
                total = 0

                for probability, next_state, reward in get_transitions(
                    grid, state, action
                ):
                    total += probability * (
                        reward + gamma * values[next_state]
                    )

                action_values.append(total)

            # Выбираем лучшее действие
            new_values[state] = max(action_values)

    return new_values

def solve_grid(grid):
    # Начальные значения всех клеток равны нулю
    values = {}

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] != "#":
                values[(row, col)] = 0

    # Повторяем вычисления до сходимости
    for iteration in range(1, max_iterations + 1):
        new_values = value_iteration_step(grid, values)

        # Наибольшее изменение за итерацию
        delta = max(
            abs(new_values[state] - values[state])
            for state in values
        )

        values = new_values

        if delta < tolerance:
            return values, iteration, delta, True

    # Если за 10000 итераций сходимость не достигнута
    return values, max_iterations, delta, False

def get_policy(grid, values):
    # Стрелки для направлений
    arrows = {
        "Up": "↑",
        "Down": "↓",
        "Left": "←",
        "Right": "→"
    }

    policy = {}

    for row in range(len(grid)):
        for col in range(len(grid[0])):
            state = (row, col)
            tile = grid[row][col]

            # Стены и конечные клетки
            if tile in ["#", "G", "H"]:
                continue

            best_action = None
            best_value = float("-inf")

            # Сравниваем четыре действия
            for action in actions:
                total = 0

                for probability, next_state, reward in get_transitions(
                    grid, state, action
                ):
                    total += probability * (
                        reward + gamma * values[next_state]
                    )

                # Выбираем действие с наибольшим значением
                if total > best_value + 1e-10:
                    best_value = total
                    best_action = action

            policy[state] = best_action

    return policy

def save_maps(grid, values, policy, filename, iterations, delta):
    # Стрелки для действий
    arrows = {
        "Up": "↑",
        "Down": "↓",
        "Left": "←",
        "Right": "→"
    }

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Iterations: {iterations}\n")
        file.write(f"Final change: {delta}\n\n")

        # Сохраняем значения клеток
        file.write("VALUE MAP\n")

        for row in range(len(grid)):
            line = []

            for col in range(len(grid[0])):
                state = (row, col)

                if grid[row][col] == "#":
                    line.append("   #   ")
                else:
                    line.append(f"{values[state]:7.3f}")

            file.write(" ".join(line) + "\n")

        # Сохраняем оптимальные действия
        file.write("\nPOLICY MAP\n")

        for row in range(len(grid)):
            line = []

            for col in range(len(grid[0])):
                tile = grid[row][col]
                state = (row, col)

                if tile in ["#", "G", "H"]:
                    line.append(tile)
                else:
                    line.append(arrows[policy[state]])

            file.write(" ".join(line) + "\n")

def simulate_episode(grid, policy, seed):
    # Отдельный генератор для воспроизводимости
    rng = random.Random(seed)

    # Находим стартовую клетку S
    start = next(
        (row, col)
        for row in range(len(grid))
        for col in range(len(grid[0]))
        if grid[row][col] == "S"
    )

    state = start
    discounted_return = 0.0

    for step in range(100):
        action = policy[state]
        transitions = get_transitions(grid, state, action)

        # Выбираем переход с учётом вероятностей
        choice = rng.random()
        cumulative = 0.0

        for probability, next_state, reward in transitions:
            cumulative += probability

            if choice < cumulative:
                break

        # Суммируем награды с коэффициентом gamma
        discounted_return += (gamma ** step) * reward
        state = next_state

        tile = grid[state[0]][state[1]]

        if tile == "G":
            return "goal", step + 1, discounted_return

        if tile == "H":
            return "hole", step + 1, discounted_return

    return "time_limit", 100, discounted_return

def run_simulations(grid, policy, map_name):
    episodes = []
    summaries = []

    for batch_seed in [11, 22, 33]:
        batch_results = []

        for i in range(50):
            episode_seed = 1000 * batch_seed + i

            outcome, steps, discounted_return = simulate_episode(
                grid, policy, episode_seed
            )

            result = {
                "map": map_name,
                "batch_seed": batch_seed,
                "episode": i + 1,
                "episode_seed": episode_seed,
                "outcome": outcome,
                "steps": steps,
                "discounted_return": discounted_return
            }

            episodes.append(result)
            batch_results.append(result)

        # Статистика одной партии
        goals = sum(r["outcome"] == "goal" for r in batch_results)
        holes = sum(r["outcome"] == "hole" for r in batch_results)
        time_limits = sum(r["outcome"] == "time_limit" for r in batch_results)

        mean_steps = sum(r["steps"] for r in batch_results) / 50
        mean_return = sum(
            r["discounted_return"] for r in batch_results
        ) / 50

        summaries.append({
            "map": map_name,
            "batch_seed": batch_seed,
            "goals": goals,
            "holes": holes,
            "time_limits": time_limits,
            "mean_steps": round(mean_steps, 3),
            "mean_discounted_return": round(mean_return, 3)
        })

    return episodes, summaries

def check_environment():
    checks = []

    # Граница карты
    checks.append((
        "Boundary",
        move(original_map, (2, 0), "Left") == (2, 0)
    ))

    # Стена
    checks.append((
        "Wall",
        move(original_map, (2, 1), "Up") == (2, 1)
    ))

    # Вероятности льда
    ice_transitions = get_transitions(original_map, (1, 2), "Up")
    probability_sum = sum(t[0] for t in ice_transitions)

    checks.append((
        "Ice probabilities",
        abs(probability_sum - 1.0) < 1e-10
    ))

    # Награды за вход в разные клетки
    mud = get_transitions(original_map, (0, 0), "Right")
    sand = get_transitions(extended_map, (2, 0), "Right")
    water = get_transitions(extended_map, (2, 2), "Right")

    checks.append(("Mud reward", mud[0][2] == -3))
    checks.append(("Sand reward", sand[0][2] == -2))
    checks.append(("Water reward", water[0][2] == -5))

    # После завершения переходов и наград больше нет
    checks.append((
        "Goal terminal",
        get_transitions(original_map, (0, 3), "Left") == []
    ))

    checks.append((
        "Hole terminal",
        get_transitions(original_map, (1, 3), "Left") == []
    ))

    return checks

print("\nMovement tests:")

# Попытка выйти за левую границу
print("Boundary:", move(original_map, (2, 0), "Left"))

# Попытка войти в стену
print("Wall:", move(original_map, (2, 1), "Up"))

# Переходы со льда
print("Ice:", get_transitions(original_map, (1, 2), "Up"))

# Начальные значения V0 = 0
values = {}

for row in range(len(original_map)):
    for col in range(len(original_map[0])):
        if original_map[row][col] != "#":
            values[(row, col)] = 0

# Первая и вторая итерации
v1 = value_iteration_step(original_map, values)
v2 = value_iteration_step(original_map, v1)

print("\nV1:")
for row in range(len(original_map)):
    print([
        "#" if original_map[row][col] == "#"
        else round(v1[(row, col)], 2)
        for col in range(len(original_map[0]))
    ])

print("\nRequested V2:")
for state in [(0, 1), (0, 2), (1, 2)]:
    print(state, "=", round(v2[state], 2))

# Решаем исходную карту
final_values, iterations, delta, converged = solve_grid(original_map)

print("\nVALUE ITERATION RESULTS")
print("Converged:", converged)
print("Iterations:", iterations)
print("Final change:", delta)

print("\nFinal value map:")
for row in range(len(original_map)):
    print([
        "#" if original_map[row][col] == "#"
        else round(final_values[(row, col)], 3)
        for col in range(len(original_map[0]))
    ])

# Получаем оптимальную стратегию
policy = get_policy(original_map, final_values)

arrows = {
    "Up": "↑",
    "Down": "↓",
    "Left": "←",
    "Right": "→"
}

print("\nOPTIMAL POLICY")

for row in range(len(original_map)):
    line = []

    for col in range(len(original_map[0])):
        tile = original_map[row][col]
        state = (row, col)

        if tile in ["#", "G", "H"]:
            line.append(tile)
        else:
            line.append(arrows[policy[state]])

    print(" ".join(line))

# Сохраняем результаты исходной карты
os.makedirs("outputs", exist_ok=True)

save_maps(
    original_map,
    final_values,
    policy,
    "outputs/part_c_original_maps.txt",
    iterations,
    delta
)

print("\nOriginal maps saved successfully.")

# Решаем расширенную карту
extended_values, extended_iterations, extended_delta, extended_converged = solve_grid(
    extended_map
)

extended_policy = get_policy(extended_map, extended_values)

print("\nEXTENDED MAP RESULTS")
print("Converged:", extended_converged)
print("Iterations:", extended_iterations)
print("Final change:", extended_delta)

print("\nExtended value map:")
for row in range(len(extended_map)):
    print([
        "#" if extended_map[row][col] == "#"
        else round(extended_values[(row, col)], 3)
        for col in range(len(extended_map[0]))
    ])

print("\nExtended optimal policy:")
for row in range(len(extended_map)):
    line = []

    for col in range(len(extended_map[0])):
        tile = extended_map[row][col]
        state = (row, col)

        if tile in ["#", "G", "H"]:
            line.append(tile)
        else:
            line.append(arrows[extended_policy[state]])

    print(" ".join(line))

# Сохраняем результаты расширенной карты
save_maps(
    extended_map,
    extended_values,
    extended_policy,
    "outputs/part_c_extended_maps.txt",
    extended_iterations,
    extended_delta
)

print("\nExtended maps saved successfully.")

print("\nSIMULATION TEST")

result = simulate_episode(original_map, policy, 11000)

print("Outcome:", result[0])
print("Steps:", result[1])
print("Discounted return:", round(result[2], 3))

# Запускаем симуляции для обеих карт
original_episodes, original_summary = run_simulations(
    original_map, policy, "original"
)

extended_episodes, extended_summary = run_simulations(
    extended_map, extended_policy, "extended"
)

all_episodes = original_episodes + extended_episodes
all_summaries = original_summary + extended_summary

# Сохраняем результаты отдельных эпизодов
with open("outputs/part_c_episodes.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=all_episodes[0].keys())
    writer.writeheader()
    writer.writerows(all_episodes)

# Сохраняем итоговую статистику
with open("outputs/part_c_summary.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=all_summaries[0].keys())
    writer.writeheader()
    writer.writerows(all_summaries)

print("\nPART C SIMULATION SUMMARY")

for result in all_summaries:
    print(result)

print("\nTotal episodes:", len(all_episodes))
print("Summary rows:", len(all_summaries))
print("Simulation results saved successfully.")

# Проверяем правила среды
checks = check_environment()

print("\nENVIRONMENT CHECKS")

with open("outputs/part_c_checks.txt", "w", encoding="utf-8") as file:
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        line = f"{name}: {status}"

        print(line)
        file.write(line + "\n")

print("\nChecks saved successfully.")
