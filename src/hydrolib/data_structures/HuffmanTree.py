from ..utils.ProbabilityCounter import ProbabilityCounter


def get_probabilities(data):
    """
    Returns a dictionary of probabilities for each character in the data
    """
    pc = ProbabilityCounter()
    for i in data:
        pc.increment(i, 1)
    return pc.probabilities()


def get_probabilities_dict(data):
    """
    Returns a dictionary of probabilities for each character in the data
    """
    pc = ProbabilityCounter()
    for i in data:
        pc.increment(i, 1)
    return pc.proabilities_dict()


class HuffmanNode:
    def __init__(self):
        self.left = None
        self.right = None
        self.value = None
        self.probability = None

    def is_leaf(self):
        return self.left is None and self.right is None

    # >
    def __gt__(self, other):
        return self.probability > other.probability

    def __lt__(self, other):
        return self.probability < other.probability

    # ==
    def __eq__(self, other):
        return self.probability == other.probability

    def __str__(self):
        return f"{self.value}"

    __repr__ = __str__


class HuffmanTree:
    def __init__(self):
        self.root = None

    def build_tree(self, probabilities: dict):
        priority_queue: list[HuffmanNode] = []
        for char, probability in probabilities.items():
            node = HuffmanNode()
            node.value = char
            node.probability = probability
            priority_queue.append(node)

        while len(priority_queue) > 1:
            priority_queue.sort()
            node1 = priority_queue.pop(0)
            node2 = priority_queue.pop(0)

            prob1 = node1.probability
            prob2 = node2.probability

            new_node = HuffmanNode()
            new_node.left = node1
            new_node.right = node2
            new_node.probability = prob1 + prob2
            priority_queue.append(new_node)

        root = priority_queue.pop()
        self.root = root

    def _walk(self, node, path):
        if node.is_leaf():
            yield path, node.value
        else:
            yield from self._walk(node.left, path + '0')
            yield from self._walk(node.right, path + '1')

    def walk(self):
        return self._walk(self.root, '')


def get_huffman_codes(huffman_tree):
    return dict(huffman_tree.walk())


def get_huffman_codes_dict(huffman_tree):
    return dict(map(lambda x: (x[1], x[0]), huffman_tree.walk()))


def compress(data):
    probabilities = get_probabilities_dict(data)
    huffman_tree = HuffmanTree()
    huffman_tree.build_tree(probabilities)
    codes = get_huffman_codes_dict(huffman_tree)

    res = ''
    for char in data:
        res += codes[char]

    return res


def decompress(data, huffman_tree: HuffmanTree):
    res = ''
    current_code = huffman_tree.root
    for char in data:
        current_code = current_code.left if char == '0' else current_code.right
        if current_code.is_leaf():
            res += current_code.value
            current_code = huffman_tree.root

    return res


if __name__ == '__main__':
    test_str = "aaaaabcdef"
    huffman_tree = HuffmanTree()
    probabilities = get_probabilities_dict(test_str)
    huffman_tree.build_tree(probabilities)

    print("Test string:", repr(test_str))
    print(probabilities)

    print(*get_huffman_codes(huffman_tree).items(), sep='\n')

    compression = compress(test_str)
    print(compression)

    decompression = decompress(compression, huffman_tree)
    print(decompression)
