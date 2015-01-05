class FixArray:

    def __init__(self, array):
        self.fix = array[0]
        self.unfix = array[1:]

    def rotate(self):
        aux = self.unfix[:(len(self.unfix) - 1)]
        aux.insert(0, self.unfix[len(self.unfix) - 1])
        self.unfix = aux

    def rotate_n(self, n=1):
        for i in xrange(0, n):
            self.rotate()

    def __getitem__(self, key):
        if key == 0:
            return self.fix
        else:
            return self.unfix[key - 1]

    def __str__(self):
        return 'fix ' + str(self.fix) + ' unfixed ' + str(self.unfix)