
# Hanoi Moves

import Queue


class Peg(object):
    def __init__(self, discs):
        super(Peg, self).__init__()
        self._discs = list(discs)

    def remove_top(self):
        return Peg(self._discs[:-1])

    def put_top(self, disc):
        cpy = self._discs[:]
        cpy.append(disc)
        return Peg(cpy)

    @property
    def top_disc(self):
        return self._discs[-1]

    @property
    def num_discs(self):
        return len(self._discs)

    def discs_bottom_up(self):
        for d in self._discs:
            yield d

    def __eq__(self, other):
        return tuple(self._discs) == tuple(other._discs)

    def __ne__(self, other):
        return not self == other

    def __contains__(self, disc):
        return disc in self._discs

    def __hash__(self):
        return hash(tuple(self._discs))


class Configuration(object):
    def __init__(self, pegs, dist=0, parent_move=None):
        super(Configuration, self).__init__()
        self._pegs = list(pegs)
        self.dist = dist
        self.parent_move = parent_move

    def get_valid_moves(self):
        for fi, from_peg in enumerate(self._pegs):
            for ti, to_peg in enumerate(self._pegs):
                if fi == ti or from_peg.num_discs == 0:
                    continue
                if (to_peg.num_discs == 0 or
                        from_peg.top_disc <= to_peg.top_disc):
                    yield Move(self, fi, ti)

    def move(self, move):
        """Assumes move is legal"""
        old_from = self._pegs[move.frm]
        old_to = self._pegs[move.to]
        disc = old_from.top_disc
        new_from = old_from.remove_top()
        new_to = old_to.put_top(disc)

        new_pegs = list(self._pegs)
        new_pegs[move.frm] = new_from
        new_pegs[move.to] = new_to

        return Configuration(new_pegs, self.dist + 1, move)

    def lower_bound(self, other):
        """Returns lower bound on number of moves necessary to
        transform into other configuration"""
        # Find the lowest disc in each peg that is placed wrong
        # The cost of fixing that peg includes at minimum moving that
        # disc and all above
        cost = 0
        for peg, other_peg in zip(self._pegs, other._pegs):
            for height, disc in enumerate(peg.discs_bottom_up()):
                if not disc in other_peg:
                    cost += peg.num_discs - height
                    # goto next peg
                    break
        return cost

    def __eq__(self, other):
        return all(sp == op for sp, op in zip(self._pegs, other._pegs))

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(tuple(self._pegs))


class Move(object):
    def __init__(self, cfg, frm, to):
        super(Move, self).__init__()
        self.cfg = cfg
        self.frm = frm
        self.to = to


def solve(start_cfg, end_cfg, max_steps=7):
    configurations = Queue.PriorityQueue()
    configurations.put((start_cfg.dist, start_cfg))
    visited = set()

    # Best-first Search
    while not configurations.empty():
        cfg = configurations.get()[1]
        visited.add(cfg)

        new_cfgs = [cfg.move(m) for m in cfg.get_valid_moves()]
        new_cfgs = [(c, c.lower_bound(end_cfg)) for c in new_cfgs]
        candidates = [(c, lb) for c, lb in new_cfgs
                      if not c in visited and c.dist + lb <= max_steps]

        for c, lb in candidates:
            if c == end_cfg:
                m = c.parent_move
                solution = []
                while m is not None:
                    solution.append(m)
                    m = m.cfg.parent_move
                solution.reverse()
                return solution
            configurations.put((c.dist + lb, c))

    return None


def parse_configuration(cfg_str, num_discs, num_pegs):
    cfg_nums = [int(x) for x in cfg_str.split(' ')]
    cfg = [[] for i in range(num_pegs)]
    for i, peg in enumerate(reversed(cfg_nums)):
        disc = num_discs - i
        cfg[peg-1].append(disc)
    cfg = Configuration([Peg(x) for x in cfg])
    return cfg


def parse_problem(input):
    constraints, start, goal = (s.strip() for s in input.split('\n'))
    num_discs, num_pegs = [int(x) for x in constraints.split(' ')]

    start_cfg = parse_configuration(start, num_discs, num_pegs)
    goal_cfg = parse_configuration(goal, num_discs, num_pegs)

    return start_cfg, goal_cfg


def output_solution(solution):
    for m in solution:
        print "Move", m.frm+1, "to", m.to+1


def run(problem):
    start, end = parse_problem(problem)
    solution = solve(start, end)
    if solution is not None:
        output_solution(solution)
    else:
        print "No solution found"


def main():
    problem = """6 4
            4 2 4 3 1 1
            1 1 1 1 1 1"""
    run(problem)

if __name__ == '__main__':
    main()
