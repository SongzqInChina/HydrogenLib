def d1(value, lenght):
    return [value for i in range(lenght)]


def d2(value, lenght, width):
    return [d1(value, width) for i in range(lenght)]


def d3(value, lenght, width, height):
    return [d2(value, lenght, width) for i in range(height)]


def d1_init(ls, value):
    lenght = len(ls)
    return d1(value, lenght)


def d2_init(ls, value):
    lenght = len(ls)
    width = len(ls[0])
    return d2(value, lenght, width)


def d3_init(ls, value):
    lenght = len(ls)
    width = len(ls[0])
    height = len(ls[0][0])
    return d3(value, lenght, width, height)


def sub(list1, list2):
    # is lst1 in lst2
    return list1 in list2


def parent(list1, list2):
    # is lst1 of lst2
    return list2 in list1


def match(list1, list2):
    return list1 == list2


def indexs_of(lst, indexs=None):
    if indexs is None:
        return []
    return [lst[i] for i in indexs]


def hasindex(iterable, index):
    if index < 0:
        index += len(iterable)
    return len(iterable) > index
