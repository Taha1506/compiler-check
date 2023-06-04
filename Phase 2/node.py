class Node:
    def __init__(self, nxt=None, star=False, terminal=None, error=None):
        self.nxt = nxt
        self.star = star
        self.terminal = terminal
        self.error = error

    def is_star(self):
        return self.star

    def is_terminal(self):
        return self.terminal

    def get_next(self, char):
        return self.nxt(char)

