def displayTable(orders):
    from collections import defaultdict
    foods = set()
    tables = defaultdict(lambda: defaultdict(int))
    for name, table, food in orders:
        foods.add(food)
        tables[int(table)][food] += 1
    food_list = sorted(foods)
    res = [["Table"] + food_list]
    for t in sorted(tables):
        res.append([str(t)] + [str(tables[t][f]) for f in food_list])
    return res
