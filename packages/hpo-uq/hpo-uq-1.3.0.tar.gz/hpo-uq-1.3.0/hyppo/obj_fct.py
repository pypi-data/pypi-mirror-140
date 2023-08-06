# Externals
import numpy
from sklearn.metrics import mean_squared_error

def calculate_outer_loss(losses,obj=None,**kwargs):
    if obj==None:
        return losses
    else:
        return eval(obj)

def sigmoid(losses,**kwargs):
    outer_losses = 1/(1 + numpy.exp(-losses))
    return outer_losses

def mse(y_real, y_predicted):
    value = mean_squared_error(numpy.squeeze(y_real), numpy.squeeze(y_predicted))
    return value

