from src.games.nnet_agent import NeuralNetAgent
import keras.layers as layers
import keras.models as models
import keras.optimizers as optimiszers
import numpy as np
import os


class ReversiNNetAgent(NeuralNetAgent):
    def __init__(self, game, args):
        self.nnet_args = args
        self.nnet = ReversiNNet(game=game, args=args)
        self.board_size = game.get_board_size()
        self.action_size = game.get_action_size()

    def predict(self, board):
        board = board[np.newaxis, :, :]
        pi, v = self.nnet.model.predict(board)
        print('predict: ', pi, v)
        return pi[0], v

    def train(self, examples):
        """
         examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        self.nnet.model.fit(x=input_boards, y=[target_pis, target_vs], batch_size=self.nnet_args.batch_size,
                            epochs=self.nnet_args.epochs)

    def save_checkpoint(self, filepath):
        if os.path.exists(filepath):
            print('检测到该路径已存在 model，是否将其覆盖？ [Y/n]')
            option = input().strip().lower()
            if option == 'n':
                return
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, filepath):
        if not os.path.exists(filepath):
            raise "未找到 model %s" % filepath
        self.nnet.model.load_weights(filepath)


class ReversiNNet(object):
    def __init__(self, game, args):
        # game params
        self.board_size = game.get_board_size()
        self.action_size = game.get_action_size()
        self.nnet_args = args

        # Neural Net
        self.input_boards = layers.Input(shape=self.board_size)  # s: batch_size x board_x x board_y

        x_image = layers.Reshape((self.board_size[0], self.board_size[1], 1))(
            self.input_boards)  # batch_size  x board_x x board_y x 1
        h_conv1 = layers.Activation('relu')(layers.BatchNormalization(axis=3)(
            layers.Conv2D(self.nnet_args.num_channels, 3, padding='same', use_bias=False)(
                x_image)))  # batch_size  x board_x x board_y x num_channels
        h_conv2 = layers.Activation('relu')(layers.BatchNormalization(axis=3)(
            layers.Conv2D(self.nnet_args.num_channels, 3, padding='same', use_bias=False)(
                h_conv1)))  # batch_size  x board_x x board_y x num_channels
        h_conv3 = layers.Activation('relu')(layers.BatchNormalization(axis=3)(
            layers.Conv2D(self.nnet_args.num_channels, 3, padding='valid', use_bias=False)(
                h_conv2)))  # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4 = layers.Activation('relu')(layers.BatchNormalization(axis=3)(
            layers.Conv2D(self.nnet_args.num_channels, 3, padding='valid', use_bias=False)(
                h_conv3)))  # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4_flat = layers.Flatten()(h_conv4)
        s_fc1 = layers.Dropout(self.nnet_args.dropout)(layers.Activation('relu')(
            layers.BatchNormalization(axis=1)(layers.Dense(1024, use_bias=False)(h_conv4_flat))))  # batch_size x 1024
        s_fc2 = layers.Dropout(self.nnet_args.dropout)(
            layers.Activation('relu')(
                layers.BatchNormalization(axis=1)(layers.Dense(512, use_bias=False)(s_fc1))))  # batch_size x 1024
        self.pi = layers.Dense(self.action_size, activation='softmax', name='pi')(
            s_fc2)  # batch_size x self.action_size
        self.v = layers.Dense(1, activation='tanh', name='v')(s_fc2)  # batch_size x 1

        self.model = models.Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'],
                           optimizer=optimiszers.Adam(self.nnet_args.lr))
