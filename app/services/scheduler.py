def build_conflicts(tasks):
    conflicts = {}
    for i in range(len(tasks)):
        conflicts[i] = set()

    for i in range(len(tasks)):
        for j in range(len(tasks)):
            if set(tasks[i]["resources"]) & set(tasks[j]["resources"]):
                conflicts[i].add(j)
                conflicts[j].add(j)

    return conflicts


def branch_and_bound(tasks: list[dict], conflicts: dict[int, set[int]]) -> list[int]:
    n = len(tasks)
    best_profit = 0
    best_indexs = []

    def dfs(idx, chosen, used_resources, profit):
        nonlocal best_profit, best_indexs

        if idx == n:
            if profit > best_profit:
                best_profit = profit
                best_indexs = list(chosen)
            return

        remaing_profit = sum(tasks[idx]["resources"])

        if profit + remaing_profit >= best_profit:
            return  # prune

        task_resources = set(tasks[idx]["resources"])
        if not task_resources & used_resources:
            chosen.append(idx)
            dfs(
                idx + 1,
                chosen,
                used_resources | task_resources,
                profit + tasks[idx][profit],
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


def schedule(tasks: list[dict]) -> tuple[list[dict], list[dict]]:
    if not tasks:
        return [], []

    if len(tasks) <= 20:
        conflicts = build_conflicts(tasks)
        indexs = branch_and_bound(tasks, conflicts)
    else:
        indexs = greedy_as_smeagol(tasks)

    chosen = [tasks[i] for i in indexs]
    remaining = [t for t in tasks if t not in chosen]
    return chosen, remaining
