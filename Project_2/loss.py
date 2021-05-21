import torch

from core import HyperCube, ones_like


class LossMSE:

    def __call__(self, input_, target):
        """
        Mean Squared Error [MSE]
        This is the call function for LossMSE and compute sum(1/2*(IN - Y)**2)

        :param input_: HyperCube corresponding to IN
        :param target: Target HyperCube
        :return: The MSE loss between the predicted value and the target
        """
        return HyperCube(1 / 2 * ((input_.value - target.value) ** 2).sum(dim=0), grad_fn=LossMSEGradFN(input_, target))

    @staticmethod
    def param():
        """

        :return: Empty list because loss does not have parameters
        """
        return []


class LossMSEGradFN:
    def __init__(self, input_, target):
        self.target = target
        self.input_ = input_

    def backward(self, output_grad):
        """
        Backward method for LossMSEGradFN, where we compute the derivative
        :param output_grad: The gradient w.r.t the output of the layer
        """
        input_grad = (self.input_.value - self.target.value) * output_grad
        self.input_.backward(input_grad)
        self.target.backward(-input_grad)


class LossBCE:

    def __call__(self, input_, target):
        """
        Call to compute the BCE loss as defined in the report

        :param input_: Input HyperCube
        :param target: Target HyperCube
        :return: The Binary Cross Entropy loss
        """
        assert torch.all(input_.value >= 0) and torch.all(input_.value <= 1), "Input values must be between [0,1]"

        return HyperCube(-(target.value * input_.value.log().clamp(-100, float("inf")) + (1 - target.value) * (
                1 - input_.value).log().clamp(-100, float("inf"))).sum(dim=0),
                         grad_fn=LossBCEGradFN(input_, target))

    @staticmethod
    def param():
        """

        :return: Empty list as loss does not have parameters
        """
        return []


class LossBCEGradFN:

    def __init__(self, input_, target):
        """
        GradFN class for LossBCE

        :param input_:  Input HyperCube
        :param target: Target HyperCube
        """
        self.input_ = input_
        self.target = target

    def backward(self, output_grad):
        x = self.input_.value
        y = self.target.value
        eps = ones_like(x) * 1e-12
        input_grad = ((x - y) / ((1 - x) * x).maximum(eps)) * output_grad
        self.input_.backward(input_grad)
        self.target.backward((-x.log() + (1 - x).log()) * output_grad)