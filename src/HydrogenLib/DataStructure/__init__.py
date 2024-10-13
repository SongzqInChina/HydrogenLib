from . import Tree, HuffmanTree, Graph, BplusTree


class Stack:
    def __init__(self, lst=None):
        self.lst = [] if lst is None else lst

    def push(self, data):
        self.lst.append(data)

    def pop(self):
        return self.lst.pop() if not self.empty() else None

    def size(self):
        return len(self.lst)

    def empty(self):
        return self.size() == 0

    def top(self):
        return self.lst[-1] if not self.empty() else None

    @property
    def front(self):
        return self.lst[-1] if not self.empty() else None

    @front.setter
    def front(self, data):
        if not self.empty():
            self.lst[-1] = data

    def __str__(self):
        return str(self.lst)

    def __iter__(self):
        return iter(self.lst)

    def __getitem__(self, item):
        return self.lst[item]

    def __len__(self):
        return len(self.lst)

    def __setitem__(self, key, value):
        self.lst[key] = value


class Heap:
    def __init__(self):
        self.heap = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left_child(self, i):
        return 2 * i + 1

    def _right_child(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _heapify_down(self, index):
        left = self._left_child(index)
        right = self._right_child(index)
        smallest = index

        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left

        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != index:
            self._swap(index, smallest)
            self._heapify_down(smallest)

    def _heapify_up(self, index):
        parent = self._parent(index)
        if index > 0 and self.heap[parent] > self.heap[index]:
            self._swap(index, parent)
            self._heapify_up(parent)

    def insert(self, value):
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)

    def extract_min(self):
        if not self.heap:
            raise IndexError("Heap is empty.")
        min_val = self.heap[0]
        last_val = self.heap.pop()
        if self.heap:
            self.heap[0] = last_val
            self._heapify_down(0)
        return min_val

    def peek(self):
        if not self.heap:
            raise IndexError("Heap is empty.")
        return self.heap[0]
