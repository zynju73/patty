#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成 bottles 域的 problem.pddl。

用法示例：
    python generate_bottle.py --num-bottles 5 --total-litres 20 \
        --output problem_random.pddl
"""

import argparse
import random
from pathlib import Path


def random_partition(total: int, n: int) :
    """把 total 随机拆成 n 份非负整数，和为 total。"""
    if n <= 0:
        raise ValueError("n must be > 0")
    parts = []
    remaining = total
    for i in range(n - 1):
        v = random.randint(0, remaining)
        parts.append(v)
        remaining -= v
    parts.append(remaining)
    random.shuffle(parts)
    return parts


def balanced_partition(total: int, n: int, shuffle: bool = True):
    """把 total 尽量均匀地拆成 n 份非负整数，和为 total。"""
    if n <= 0:
        raise ValueError("n must be > 0")
    base = total // n
    remainder = total % n
    parts = [base] * n
    indices = list(range(n))
    if shuffle:
        random.shuffle(indices)
    for idx in indices[:remainder]:
        parts[idx] += 1
    return parts


def generate_problem(num_bottles: int,
                     total_litres: int,
                     problem_name: str = "random-bottles",
                     output_path: str = "problem.pddl",
                     seed: int = None,
                     mode: str = "hard") -> None:
    if num_bottles <= 0:
        raise ValueError("num_bottles 必须 > 0")
    if total_litres < 0:
        raise ValueError("total_litres 不能为负")

    if seed is not None:
        random.seed(seed)

    # 瓶子命名：b1, b2, ..., bN
    bottles = [f"b{i+1}" for i in range(num_bottles)]

    # 按 domain_bottle.pddl 中的类型层次：
    #   bottleleft, bottleright - bottle
    # 这里简单地前一半当作 bottleleft，后一半当作 bottleright
    half = max(1, num_bottles // 2)
    left_bottles = bottles[:half]
    right_bottles = bottles[half:] if half < num_bottles else bottles

    # 生成各瓶初始 litres，和为 total_litres。
    # hard:
    #   把水尽量均匀放在 left_bottles，right_bottles 初始为 0。
    #   目标把 left 的水全部转移到 right，因此最少 pour 次数 = total_litres。
    # random:
    #   保留旧逻辑：总水量随机分布到所有瓶子，再随机决定每个 left 倒出多少。
    litres_per_bottle = [0] * num_bottles
    n_left = len(left_bottles)

    if mode == "hard":
        left_amounts = balanced_partition(total_litres, n_left)
        for i, amount in enumerate(left_amounts):
            litres_per_bottle[i] = amount
    elif mode == "random":
        if total_litres >= n_left:
            # 先保证每个 left 至少有 1 升
            for i in range(n_left):
                litres_per_bottle[i] = 1

            remaining = total_litres - n_left
            if remaining > 0:
                # 把剩余部分随机分配给所有瓶子
                extra = random_partition(remaining, num_bottles)
                for i in range(num_bottles):
                    litres_per_bottle[i] += extra[i]
        else:
            # 总量不足以让所有 left 都 >=1：尽量多地给 left 分配 1 升
            # 只在 left_bottles 中选 total_litres 个位置，每个加 1（如果 total_litres < n_left）
            indices = random.sample(range(n_left), total_litres)
            for idx in indices:
                litres_per_bottle[idx] += 1
    else:
        raise ValueError(f"未知 mode: {mode}")

    # 生成 (:objects) 区块
    objects_lines = []
    for lb in left_bottles:
        objects_lines.append("    " + lb + " - bottleleft")
    for rb in right_bottles:
        objects_lines.append("    " + rb + " - bottleright")
    objects_block = "\n".join(objects_lines)

    # 生成 (:init) 区块
    init_lines = []
    # 可以选择全部初始为 capped 或全部不 capped，这里全部 capped
    for b in bottles:
        init_lines.append(f"    (capped {b})")
    for b, v in zip(bottles, litres_per_bottle):
        init_lines.append(f"    (= (litres {b}) {v})")
    init_block = "\n".join(init_lines)

    # 初始体积按瓶子名建表
    init_map = {b: v for b, v in zip(bottles, litres_per_bottle)}

    if mode == "hard":
        left_transfers = [init_map[b] for b in left_bottles]
        total_transfer = sum(left_transfers)
        right_extras = balanced_partition(total_transfer, len(right_bottles))
    else:
        # left 侧倒出量
        left_transfers = []
        for b in left_bottles:
            v = init_map[b]
            if v <= 0:
                t = 0
            else:
                # 至少倒出 1 单位，最多倒出全部
                t = random.randint(1, v)
            left_transfers.append(t)
        total_transfer = sum(left_transfers)

        # right 侧接收量
        right_extras = [0] * len(right_bottles)
        if right_bottles and total_transfer > 0:
            m = len(right_bottles)
            if total_transfer >= m:
                # 先保证每个 right 至少 +1
                base = [1] * m
                remaining = total_transfer - m
                extra = [0] * m
                for _ in range(remaining):
                    idx = random.randrange(m)
                    extra[idx] += 1
                right_extras = [b + e for b, e in zip(base, extra)]
            else:
                # total_transfer < m：随机选择 total_transfer 个 right，每个加 1
                indices = random.sample(range(m), total_transfer)
                for idx in indices:
                    right_extras[idx] += 1

    # 计算 goal 中每个瓶子的 litres
    goal_map = {}
    # left: 减去倒出的量
    for b, t in zip(left_bottles, left_transfers):
        goal_map[b] = init_map[b] - t
    # right: 加上接收的量
    for b, e in zip(right_bottles, right_extras):
        init_v = init_map[b]
        goal_map[b] = init_v + e

    # 若某个 right 同时也是 left（例如只有 1 个瓶子时的边界情况），
    # 以最后一次赋值为准，但仍保证总量守恒：
    assert sum(init_map.values()) == sum(goal_map.values())

    goal_lines = []
    for b in bottles:
        goal_lines.append(f"    (= (litres {b}) {goal_map[b]})")
    goal_block = "\n".join(goal_lines)

    problem_pddl = f"""(define (problem {problem_name})
  (:domain bottles)

  (:objects
{objects_block}
  )

  (:init
{init_block}
  )

  (:goal
  (and
{goal_block}
  )
  )
)
"""

    out_path = Path(output_path)
    out_path.write_text(problem_pddl, encoding="utf-8")
    print(f"problem 写入: {out_path.resolve()}")
    print(f"mode: {mode}, total_transfer: {total_transfer}, expected_min_pours: {total_transfer}")


def main():
    parser = argparse.ArgumentParser(description="随机生成 bottles 域的 problem.pddl")
    parser.add_argument("--num-bottles", type=int, required=True,
                        help="瓶子数量（总数）")
    parser.add_argument("--total-litres", type=int, required=True,
                        help="液体总量（整数）")
    parser.add_argument("--output", type=str, default="problem.pddl",
                        help="输出 problem.pddl 路径")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（可选，便于复现）")
    parser.add_argument("--name", type=str, default="random-bottles",
                        help="problem 名字（PDDL 中的名字）")
    parser.add_argument("--mode", choices=["hard", "random"], default="hard",
                        help="生成模式：hard 均匀分配并强制全部从 left 转到 right；random 使用旧随机逻辑")

    args = parser.parse_args()
    generate_problem(
        num_bottles=args.num_bottles,
        total_litres=args.total_litres,
        problem_name=args.name,
        output_path=args.output,
        seed=args.seed,
        mode=args.mode,
    )


if __name__ == "__main__":
    main()