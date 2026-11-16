import gymnasium as gym  # Библиотека для FrozenLake
import random 
import csv
import os

def fixed_policy(state):
    # Направления для каждой клетки карты
    actions = [
        1, 2, 1, 0,
        1, 0, 1, 0,
        2, 2, 1, 0,
        0, 2, 2, 0
    ]
    return actions[state]  # Возвращаем действие


def run_episode(env, seed, policy):
    # Начинаем игру с заданным seed
    state, info = env.reset(seed=seed)

    rng = random.Random(seed)  # Генератор случайных действий
    total_reward = 0  # Общая награда
    steps = 0  # Количество шагов
    outcome = "time_limit"  # Результат по умолчанию

    # Максимум 100 шагов
    for step in range(100):

        # Выбираем стратегию
        if policy == "random":
            action = rng.randint(0, 3)
        else:
            action = fixed_policy(state)

        # Выполняем действие
        state, reward, terminated, truncated, info = env.step(action)

        total_reward += reward
        steps += 1

        # Проверяем завершение игры
        if terminated:
            outcome = "goal" if state == 15 else "hole"
            break

        if truncated:
            outcome = "time_limit"
            break

    return steps, total_reward, outcome


def save_trace(env, seed, policy, filename):
    # Начинаем эпизод с указанным seed
    state, info = env.reset(seed=seed)
    rng = random.Random(seed)

    # Названия направлений
    directions = ["Left", "Down", "Right", "Up"]

    # Открываем файл для записи
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Policy: {policy}\n")
        file.write(f"Seed: {seed}\n")
        file.write(f"Start state: {state}\n\n")

        # Сохраняем начальную карту
        file.write(env.render() + "\n")

        # Записываем каждый шаг
        for step in range(1, 101):

            # Выбираем действие
            if policy == "random":
                action = rng.randint(0, 3)
            else:
                action = fixed_policy(state)

            # Выполняем шаг
            state, reward, terminated, truncated, info = env.step(action)

            # Сохраняем действие и новую позицию
            file.write(
                f"Step {step}: {directions[action]} -> "
                f"state {state}, reward {reward}\n"
            )

            # Сохраняем карту после шага
            file.write(env.render() + "\n")

            # Проверяем результат
            if terminated or truncated:
                if terminated:
                    outcome = "goal" if state == 15 else "hole"
                else:
                    outcome = "time_limit"

                file.write(f"Outcome: {outcome}\n")
                break
        else:
            # Если закончились 100 шагов
            file.write("Outcome: time_limit\n")

# Создаём папку для результатов
os.makedirs("outputs", exist_ok=True)

results = []

# Проверяем два режима скольжения
for slippery in [False, True]:

    # Создаём среду FrozenLake
    env = gym.make(
        "FrozenLake-v1",
        map_name="4x4",
        is_slippery=slippery
    )

    # Проверяем две стратегии
    for policy in ["random", "fixed"]:

        # Три серии экспериментов
        for batch_seed in [11, 22, 33]:

            # 50 эпизодов в каждой серии
            for i in range(50):

                # Уникальный seed эпизода
                episode_seed = 1000 * batch_seed + i

                # Запускаем одну игру
                steps, reward, outcome = run_episode(
                    env, episode_seed, policy
                )

                results.append({
                    "condition": "slippery" if slippery else "not_slippery",
                    "batch_seed": batch_seed,
                    "episode_seed": episode_seed,
                    "policy": policy,
                    "steps": steps,
                    "total_reward": reward,
                    "outcome": outcome
                })

    env.close()


# Сохраняем все эпизоды в CSV
with open("outputs/part_b_episodes.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()  # Названия столбцов
    writer.writerows(results)  # Все результаты


# Группируем результаты по условиям эксперимента
summary = []

for slippery in [False, True]:
    for policy in ["random", "fixed"]:
        for batch_seed in [11, 22, 33]:

            # Выбираем 50 эпизодов одной серии
            batch = [
                r for r in results
                if r["condition"] == ("slippery" if slippery else "not_slippery")
                and r["policy"] == policy
                and r["batch_seed"] == batch_seed
            ]

            # Считаем результаты
            goals = sum(r["outcome"] == "goal" for r in batch)
            holes = sum(r["outcome"] == "hole" for r in batch)
            time_limits = sum(r["outcome"] == "time_limit" for r in batch)

            # Вычисляем процент успеха
            success = goals / 50 * 100

            # Вычисляем среднее количество шагов
            mean_steps = sum(r["steps"] for r in batch) / 50

            # Сохраняем статистику серии
            summary.append({
                "slippery": slippery,
                "policy": policy,
                "batch_seed": batch_seed,
                "goals": goals,
                "holes": holes,
                "time_limits": time_limits,
                "success_percent": success,
                "mean_steps": mean_steps
            })

# Сохраняем итоговую таблицу
with open("outputs/part_b_summary.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

# Показываем результаты в терминале
print("\nPART B SUMMARY")

for row in summary:
    print(row)

print("\nSummary saved to outputs/part_b_summary.csv")

print("Total episodes:", len(results))
print("Summary rows:", len(summary))


# Выбираем успешный и неуспешный эпизоды
success_episode = next(r for r in results if r["outcome"] == "goal")
failed_episode = next(r for r in results if r["outcome"] == "hole")

# Сохраняем оба прохождения
for episode, filename in [
    (success_episode, "outputs/part_b_success_trace.txt"),
    (failed_episode, "outputs/part_b_failed_trace.txt")
]:
    # Определяем режим скольжения
    slippery = episode["condition"] == "slippery"

    # Создаём среду с текстовым отображением
    env = gym.make(
        "FrozenLake-v1",
        map_name="4x4",
        is_slippery=slippery,
        render_mode="ansi"
    )

    # Записываем историю прохождения
    save_trace(
        env,
        episode["episode_seed"],
        episode["policy"],
        filename
    )

    env.close()

print("Traces saved successfully.")