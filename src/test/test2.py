import numpy as np
import matplotlib.pyplot as plt
import random

x_data = np.array([338., 333., 328., 207., 226., 25., 179., 60., 208., 606.])
y_data = np.array([640., 633., 619., 393., 428., 27., 193., 66., 226., 1591.])

b = -120
w = -4
lr = 1
iteration = 100

b_lr = 0.0
w_lr = 0.0

for i in range(iteration):
    b_grad = 0
    w_grad = 0

    loss = 0.0
    for n in range(len(x_data)):
        loss += (y_data[n] - w * x_data[n] - b)**2
        w_grad += 2 * (y_data[n] - w * x_data[n] - b) * -x_data[n]
        b_grad += 2 * (y_data[n] - w * x_data[n] - b) * -1

    b_lr += b_grad**2
    w_lr += w_grad**2

    b -= lr / np.sqrt(b_lr) * b_grad
    w -= lr / np.sqrt(w_lr) * w_grad

    plt.cla()
    plt.scatter(x_data, y_data)
    plt.plot(x_data, x_data * w)
    plt.text(.5, 0, 'Loss=%.4f' % loss, fontdict={'size': 20, 'color': 'red'})
    plt.pause(0.1)
print(b, w)
