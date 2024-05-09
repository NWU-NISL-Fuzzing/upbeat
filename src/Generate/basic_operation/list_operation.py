def add_element(list1: list, list2: list):
    """合并两个列表，并去除重复元素"""

    return list(set(list1.extend(list2)))


def get_clear_list(l: list):
    """去除列表中的重复元素"""

    return list(set(l))

