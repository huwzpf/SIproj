import copy
import random
import numpy as np
from SMO import SMO

class SVM_multiclass:
    @staticmethod
    def prepare_intermediate_matrix(x):
        fp = np.memmap("intermediate.dat", dtype='float32', mode='w+', shape=(x.shape[0], x.shape[0]))
        for i in range(x.shape[0]):
            for j in range(0, i):
                fp[i, j] = fp[j, i]
            for j in range(i, x.shape[0]):
                fp[i, j] = -1 * np.transpose(x[i, :]-x[j, :]).dot(x[i, :]-x[j, :])
            print(f"intermediate matrix {i} / {x.shape[0]} done")

    def prepare_kernel_matrix(self, x, gamma):
        # load intermediate matrix containing base for calculating kernels
        for attempt in range(2):
            try:
                im = np.memmap("intermediate.dat", dtype='float32', mode='r', shape=(x.shape[0], x.shape[0]))
                break
            except FileNotFoundError:
                print("preparing intermediate matrix")
                self.prepare_intermediate_matrix(x)

        fp = np.memmap("kernels.dat", dtype='float32', mode='w+', shape=(x.shape[0], x.shape[0]))

        for i in range(x.shape[0]):
            for j in range(0, i):
                fp[i, j] = fp[j, i]
            for j in range(i, x.shape[0]):
                fp[i, j] = np.exp(im[i, j] / gamma)
            print(f"kernel matrix {i} / {x.shape[0]} done")

    def prepare_data(self, x, y, k, km="", gamma=0):
        # switch y to one hot encoding (except -1 where 0 would normally be)
        labels = np.negative(np.ones((len(y), k)))
        for i in range(len(y)):
            labels[i, y[i]] = 1
        # normalize x
        args = copy.copy(x).astype(np.float64)
        args /= (255 / 2)
        args -= 1

        for attempt in range(2):
            try:
                fp = np.memmap(km, dtype='float32', mode='r', shape=(x.shape[0], x.shape[0]))
                break
            except FileNotFoundError:
                print("preparing intermediate matrix")
                self.prepare_kernel_matrix(x, gamma)

        # prepare datasets for each SVM
        for i in range(k):
            # select points from dataset which will be used for this svm
            a = list(np.where(y == i)[0])
            sample_size = len(a)
            b = random.sample(list(np.where(y != i)[0]), sample_size)
            idx = a + b
            np.random.shuffle(idx)
            # each SVM needs args, labels and kernel matrix
            km = np.memmap("kernels" + str(i) + ".dat", dtype='float32', mode='w+', shape=(2 * sample_size, 2 * sample_size))

            for j in range(2*sample_size):
                for k in range(2*sample_size):
                    km[j, k] = fp[idx[j], idx[k]]

            np.save("args" + str(i) + ".npy", np.array([args[j, :] for j in idx]))
            np.save("labels" + str(i) + ".npy", np.array([labels[j, i] for j in idx]))

        print("done creating datasets")

    def __init__(self, x, y, k, c=1.0, gamma=100, tol=0.001, max_iters=10000):
        self.svms = []
        for attempt in range(2):
            try:
                for i in range(k):
                    labels = np.load(open("labels" + str(i) + ".npy", 'rb'))
                    args = np.load(open("args" + str(i) + ".npy", 'rb'))
                    km = np.memmap("kernels" + str(i) + ".dat", dtype='float32', mode='r',
                                                   shape=(len(labels), len(labels)))
                    self.svms.append(SMO(args, labels, c, gamma, km))
                break
            except FileNotFoundError:
                print("preparing data")
                self.prepare_data(x, y, k, "kernels1000.dat")

        print("done creating SVMs")
        i = 0
        for svm in self.svms:
            svm.train(tol, max_iters, ident=i, load=True)
            i += 1
           # print(f"trained, accuracy : {svm.train_accuracy()}")
            svm.visualize(i-1)

        print("training done")

    def test(self, args, y, k, prnt=False):
        x = copy.copy(args.reshape(args.shape[0], -1)).astype(np.float64)
        x /= (255 / 2)
        x -= 1
        count = 0
        outputs = np.zeros((len(y), k))
        results = np.zeros(len(y))
        for i in range(len(y)):
            for j in range(k):
                outputs[i, j] = self.svms[j].hypothesis(x[i, :])
            results[i] = np.argmax(outputs[i, :])
            if results[i] != y[i]:
                count += 1
            if prnt:
                print(results[i], y[i], count/(i+1))
        print(f"test results: {count/len(y)}")
        return count/len(y)
