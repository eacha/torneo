from FixArray import FixArray


class Fixture:

    def __init__(self, players, games=1):

        if 0 == len(players) % 2:
            self.player_array = FixArray(players)
        else:
            players.insert(0, -1)
            self.player_array = FixArray(players)

        self.normal_round = True
        self.number_of_player = len(players)
        self.rounds = self.number_of_player - 1
        self.numbers_of_rounds = self.rounds * games

    def generate(self):
        fixture = []
        for x in xrange(1, self.numbers_of_rounds + 1):
            fixture.append(self.generate_round())
            self.player_array.rotate()
            if x % self.rounds == 0:
                self.normal_round = not self.normal_round
        return fixture

    def generate_round(self):
        round = []
        for i in xrange(0, self.number_of_player / 2):
            if self.player_array[i] != -1 and self.player_array[i + (self.number_of_player / 2) != -1]:
                if self.normal_round:
                    round.append((self.player_array[i], self.player_array[i + (self.number_of_player / 2)]))
                else:
                    round.append((self.player_array[i + (self.number_of_player / 2)], self.player_array[i]))
        return round

class ble:

    def __init__(self, a):
        self.name = a

    def __str__(self):
        return str(self.name)

a = ['a', 'b', 'c']
b = Fixture(a)
print b.generate()