class NeuralNetAgent(object):

    def predict(self, board):
        """
        输入当前棋盘（相对），预测每个点的权值
        """
        pass

    def train(self, examples):
        """
        训练
        """
        pass

    def save_checkpoint(self, folder, filename):
        """
        保存当前的神经网络
        """
        pass

    def load_checkpoint(self, folder, filename):
        """
        加载神经网络
        """
        pass
