import torch
import torch.optim
import matplotlib.pyplot as plt
import torch.nn.functional as F

x = torch.unsqueeze(
    torch.linspace(-1, 1, 100), dim=1)  # x data (tensor), shape=(100, 1)
y = x**2 + 0.2 * torch.rand(x.size())  # noisy y data (tensor), shape=(100, 1)


# plt.scatter(x.data.numpy(), y.data.numpy())
# plt.show()
class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        self.hidden = torch.nn.Linear(n_feature, n_hidden)
        self.predict = torch.nn.Linear(n_hidden, n_output)

    def forward(self, input):
        x = F.relu(self.hidden(input))
        x = self.predict(x)
        return x


net = Net(1, 10, 1)
# print(net)

plt.ion()
plt.show()

optimizer = torch.optim.SGD(net.parameters(), lr=.2)
loss_fun = torch.nn.MSELoss()

for t in range(100):
    prediction = net(x)
    loss = loss_fun(prediction, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if t % 5 == 0:
        plt.cla()
        plt.scatter(x.data.numpy(), y.data.numpy())
        plt.plot(x.data.numpy(), prediction.data.numpy(), 'r-', lw=5)
        plt.text(
            0.5,
            0,
            'Loss=%.4f' % loss.data.numpy(),
            fontdict={
                'size': 20,
                'color': 'red'
            })
        plt.pause(0.1)
    pass
