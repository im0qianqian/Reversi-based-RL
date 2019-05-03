class Coach(object):
    """
    reinforcement learning self-play
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        pass
