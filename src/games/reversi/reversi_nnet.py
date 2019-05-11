import os
import time
from src.games.nnet_agent import NeuralNetAgent
import tensorflow as tf
# from tensorflow.python.keras.layers import *
# from tensorflow.python.keras.models import *
# from tensorflow.python.keras.optimizers import *
# from tensorflow.python.keras.callbacks import TensorBoard
from keras.layers import *
from keras.models import *
from keras.optimizers import *
from keras.callbacks import TensorBoard
import numpy as np


class NNetWrapper(NeuralNetAgent):
    def __init__(self, game, args):
        self.args = args
        self.nnet = OthelloNNet(game, args)
        self.board_x, self.board_y = game.get_board_size()
        self.action_size = game.get_action_size()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)

        tb_call_back = TensorBoard(log_dir=os.path.join(self.args.logs_folder, str(time.time())),  # log 目录
                                   histogram_freq=0,
                                   batch_size=self.args.batch_size,
                                   write_graph=True,  # 是否存储网络结构图
                                   write_grads=True,  # 是否可视化梯度直方图
                                   write_images=True,  # 是否可视化参数
                                   embeddings_freq=0,
                                   embeddings_layer_names=None,
                                   embeddings_metadata=None)

        # 使用当前的棋盘作输入，拟合 (可行点的概率，权值)
        self.nnet.model.fit(x=input_boards, y=[target_pis, target_vs], batch_size=self.args.batch_size,
                            epochs=self.args.epochs,
                            callbacks=[tb_call_back])

    def predict(self, board):
        """
        board: np array with board
        """
        # preparing input
        if self.args.use_tpu:
            # 使用 TPU 时因为有 8 个核心，所以这里的大小必须是 8 的整数倍 QAQ，没找到其他办法
            tmp = []
            for i in range(8):
                tmp.append(board)
            board = np.array(tmp)
        else:
            board = board[np.newaxis, :, :]

        # run
        pi, v = self.nnet.model.predict(board)

        # print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return pi[0], v[0]

    def save_checkpoint(self, folder, filename):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")

        self.nnet.model.save_weights(filepath)
        # if self.args.use_tpu:
        #     # 使用 TPU 时需先将 model sync 到 cpu 中再存储（这里还有 bug）
        #     model_tmp = self.nnet.model.sync_to_cpu()
        #     model_tmp.save_weights(filepath)
        # else:
        #     self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder, filename):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise ("No model in path {}".format(filepath))
        self.nnet.model.load_weights(filepath)


class OthelloNNet(object):
    def __init__(self, game, args):
        # game params
        self.board_x, self.board_y = game.get_board_size()
        self.action_size = game.get_action_size()
        self.args = args

        # Neural Net
        if args.use_tpu:
            # 使用 TPU 时这里可以在多个核心中并发提高效率
            self.input_boards = Input(shape=(self.board_x, self.board_y),
                                      batch_size=self.args.model_batch_size)  # batch_size 指定模型输入大小
        else:
            self.input_boards = Input(shape=(self.board_x, self.board_y))

        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)  # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(args.num_channels, 3, padding='same', use_bias=False)(
                x_image)))  # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(args.num_channels, 3, padding='same', use_bias=False)(
                h_conv1)))  # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(
                h_conv2)))  # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(
                h_conv3)))  # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4_flat = Flatten()(h_conv4)
        s_fc1 = Dropout(args.dropout)(Activation('relu')(
            BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv4_flat))))  # batch_size x 1024
        s_fc2 = Dropout(args.dropout)(
            Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc1))))  # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)  # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)  # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])

        if args.use_tpu:
            # 支持 TPU 训练，关键代码在这里，需要一个TPU
            self.model = tf.contrib.tpu.keras_to_tpu_model(
                self.model,
                strategy=tf.contrib.tpu.TPUDistributionStrategy(
                    tf.contrib.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])
                )
            )
        self.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'],
                           optimizer=tf.train.AdamOptimizer(learning_rate=args.lr))
