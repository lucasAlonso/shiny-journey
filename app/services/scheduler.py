def branch_and_bound(tasks: list[dict]) -> list[int]:
    n = len(tasks)
    best_profit = -1
    best_indexs = []

    def dfs(idx, chosen, used_resources, profit):
        nonlocal best_profit, best_indexs

        if idx == n:
            if profit > best_profit:
                best_profit = profit
                best_indexs = list(chosen)
            return

        remaing_profit = sum(tasks[i]["profit"] for i in range(idx, n))

        if profit + remaing_profit <= best_profit:
            return  # prune

        task_resources = set(tasks[idx]["resources"])
        if not task_resources & used_resources:
            chosen.append(idx)
            dfs(
                idx + 1,
                chosen,
                used_resources | task_resources,
                profit + tasks[idx]["profit"],
            )
            chosen.pop()

        dfs(idx + 1, chosen, used_resources, profit)

    dfs(0, [], set(), 0.0)

    return best_indexs


def greedy_as_smeagol(tasks: list[dict]) -> list[int]:
    sorted_tasks = sorted(enumerate(tasks), key=lambda x: x[1]["profit"], reverse=True)
    occupied = set()
    chosen = []
    for idx, task in sorted_tasks:
        if not set(task["resources"]) & occupied:
            chosen.append(idx)
            occupied |= set(task["resources"])
    return chosen


def schedule(tasks: list[dict]) -> tuple[list[int], list[int]]:
    if not tasks:
        return [], []

    if len(tasks) <= 20:
        chosen_indices = branch_and_bound(tasks)
    else:
        chosen_indices = greedy_as_smeagol(tasks)

    all_indices = set(range(len(tasks)))
    remaining_indices = list(all_indices - set(chosen_indices))
    return chosen_indices, remaining_indices
