from NeuralNet import NeuralNet
from SoftmaxReg import SoftmaxRegression
from LoadData import load_data, prepare_data
from SVM_multiclass import SVM_multiclass


def main():
    train_args, train_labels, test_args, test_labels = load_data()
    n = NeuralNet(784, [800], 10, [NeuralNet.ActivationType.SIGMOID, NeuralNet.ActivationType.SIGMOID])
    s = SoftmaxRegression(784, 10)
    x_train, y_train = prepare_data(train_args, train_labels)
    x_test, y_test = prepare_data(test_args, test_labels)

    print("SOFTMAX REGRESSION")
    train_and_test(s, test_labels, x_test, x_train, y_train)
    s.print_theta_as_square_matrix()
    print("NEURAL NEWTWORK")
    train_and_test(n, test_labels, x_test, x_train, y_train)
    # print("SVM")
    # s = SVM_multiclass(train_args.reshape(train_args.shape[0], -1), train_labels, 10)
    # s.test(test_args, test_labels, 10, True)


def train_and_test(model, test_labels, x_test, x_train, y_train):
    model.train(x_train, y_train)
    count = 0
    for i in range(len(test_labels)):
        prediction = model.predict(x_test[i, :].reshape(1, 784))
        if prediction == test_labels[i]:
            count += 1
    print(f"test results {count / len(test_labels)}")
    # model.plot_layer(1)


if __name__ == '__main__':
    main()
