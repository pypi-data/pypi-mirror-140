class Array:
    def __init__(self, size=10, zero=None):
        self.size = size
        self.data = size * [zero]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self)

    def check_index(self, index):
        assert 0 <= index < len(self.data), "array index out of range"

    def __setitem__(self, index, value):
        self.check_index(index)
        self.data[index] = value

    def __getitem__(self, index):
        self.check_index(index)
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __eq__(self, outro):
        if type(outro) is list:
            return self.data == outro
        return outro.data == self.data
