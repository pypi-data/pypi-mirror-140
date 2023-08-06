from collections import Iterator

class DynamicRuneArr(Iterator):
    def __init__(self, items):
        self._data = items
        self._index = 0

    def __getitem__(self, key):
        return [item.selenium_rune.get_attribute(key) for item in self._data]

    def __next__(self):
        if self._index < len(self._data):
            value = self._data[self._index]
            self._index += 1
            return value
        else:
            self._index = 0
            raise StopIteration
            
    def __len__(self):
        return len(self._data)