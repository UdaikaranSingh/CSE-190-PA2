import numpy as np
import pickle
import copy


config = {}
config['layer_specs'] = [784, 50, 10]  # The length of list denotes number of hidden layers; each element denotes number of neurons in that layer; first element is the size of input layer, last element is the size of output layer.
config['activation'] = 'sigmoid' # Takes values 'sigmoid', 'tanh' or 'ReLU'; denotes activation function for hidden layers
config['batch_size'] = 50000  # Number of training samples per batch to be passed to network
config['epochs'] = 100  # Number of epochs train the model
config['early_stop'] = True  # Implement early stopping or not
config['early_stop_epoch'] = 5  # Number of epochs for which validation loss increases to be counted as overfitting
config['L2_penalty'] = 0  # Regularization constant
config['momentum'] = False  # Denotes if momentum is to be applied or not
config['momentum_gamma'] = 0.9  # Denotes the constant 'gamma' in momentum expression
config['learning_rate'] = 0.001 # Learning rate of gradient descent algorithm

def softmax(x):
  """
  Write the code for softmax activation function that takes in a numpy array and returns a numpy array.
  """
  exps = np.exp(x)
  exps_sum = np.sum(exps)
  output = exps / exps_sum
  return output


def load_data(fname):
  """
  Write code to read the data and return it as 2 numpy arrays.
  Make sure to convert labels to one hot encoded format.
  """
  images = []
  unencoded_labels = []
  labels = []

  with open('data/' + fname, 'rb') as f:
      data_set = pickle.load(f)
      for i in data_set:
          images.append(i[0:len(i)-1])
          unencoded_labels.append(i[len(i)-1])

  for j in unencoded_labels:
      one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      one_hot[int(j)] = 1
      labels.append(one_hot)

  images = np.array(images)
  labels = np.array(labels)

  return images, labels


class Activation:
  def __init__(self, activation_type = "sigmoid"):
    self.activation_type = activation_type
    self.x = None # Save the input 'x' for sigmoid or tanh or ReLU to this variable since it will be used later for computing gradients.

  def forward_pass(self, a):
    if self.activation_type == "sigmoid":
      return self.sigmoid(a)

    elif self.activation_type == "tanh":
      return self.tanh(a)

    elif self.activation_type == "ReLU":
      return self.ReLU(a)

  def backward_pass(self, delta):
    if self.activation_type == "sigmoid":
      grad = self.grad_sigmoid()

    elif self.activation_type == "tanh":
      grad = self.grad_tanh()

    elif self.activation_type == "ReLU":
      grad = self.grad_ReLU()

    return grad * delta

  def sigmoid(self, x):
    """
    Write the code for sigmoid activation function that takes in a numpy array and returns a numpy array.
    """
    self.x = x
    output = 1 / (1 + np.exp(-self.x))
    return output

  def tanh(self, x):
    """
    Write the code for tanh activation function that takes in a numpy array and returns a numpy array.
    """
    self.x = x
    output = np.tanh(self.x)
    return output

  def ReLU(self, x):
    """
    Write the code for ReLU activation function that takes in a numpy array and returns a numpy array.
    """
    self.x = x
    output = self.x * (self.x > 0)
    return output

  def grad_sigmoid(self):
    """
    Write the code for gradient through sigmoid activation function that takes in a numpy array and returns a numpy array.
    """
    grad = self.sigmoid(self.x) * (1 - self.sigmoid(self.x))
    return grad

  def grad_tanh(self):
    """
    Write the code for gradient through tanh activation function that takes in a numpy array and returns a numpy array.
    """
    grad = (1 - np.power(self.tanh(self.x), 2))
    return grad

  def grad_ReLU(self):
    """
    Write the code for gradient through ReLU activation function that takes in a numpy array and returns a numpy array.
    """
    #need to fix RelU gradient
    grad = []
    for val in self.x[0]:
      if (val < 0):
        grad.append(0)
      else:
        grad.append(1)
    grad = np.asarray(grad)
    return grad


class Layer():
  def __init__(self, in_units, out_units):
    np.random.seed(42)
    self.w = np.random.randn(in_units, out_units)  # Weight matrix
    self.b = np.zeros((1, out_units)).astype(np.float32)  # Bias
    self.x = None  # Save the input to forward_pass in this
    self.a = None  # Save the output of forward pass in this (without activation)
    self.d_x = None  # Save the gradient w.r.t x in this
    self.d_w = None  # Save the gradient w.r.t w in this
    self.d_b = None  # Save the gradient w.r.t b in this
    self.momentum_d_w = None
    self.momentum_d_b = None

    self.count = 0

  def forward_pass(self, x):
    """
    Write the code for forward pass through a layer. Do not apply activation function here.
    """
    self.x = x
    self.a = np.matmul(x, self.w) + self.b
    #shape of self.a = (1 x out_units)
    return self.a

  def backward_pass(self, delta):
    """
    Write the code for backward pass. This takes in gradient from its next layer as input,
    computes gradient for its weights and the delta to pass to its previous layers.
    """
    if (self.count > 0):
      self.momentum_d_w = (self.d_w) * config['momentum_gamma']**self.count
      self.momentum_d_b = (self.d_b) * config['momentum_gamma']**self.count

    #add regularization term
    self.d_x = np.dot(delta, self.w.T)
    self.d_b = delta + config['L2_penalty'] * self.b
    self.d_w = np.dot(delta.T, self.x).T + config['L2_penalty'] * self.w

    self.count = self.count + 1

    return self.d_x


class Neuralnetwork():
  def __init__(self, config):
    self.layers = []
    self.x = None  # Save the input to forward_pass in this
    self.y = None  # Save the output vector of model in this
    self.targets = None  # Save the targets in forward_pass in this variable
    for i in range(len(config['layer_specs']) - 1):
      self.layers.append( Layer(config['layer_specs'][i], config['layer_specs'][i+1]) )
      if i < len(config['layer_specs']) - 2:
        self.layers.append(Activation(config['activation']))
    self.config = config

  def forward_pass(self, x, targets = None):
    """
    Write the code for forward pass through all layers of the model and return loss and predictions.
    If targets == None, loss should be None. If not, then return the loss computed.
    """
    self.x = x
    if (targets.any() == None):
      loss = None
    else:
      self.targets = targets
      curOut = self.x
      #iterarting through the layers
      for curLayer in self.layers:
        curOut = curLayer.forward_pass(curOut)
      #updating outputs
      self.y = softmax(curOut)
      
      #computed loss in different part of code
      loss = self.loss_func(self.y, self.targets)
      loss = 0

    return loss, self.y

  def loss_func(self, logits, targets):
    '''
    find cross entropy loss between logits and targets
    '''
    
    loss = - np.sum(targets * np.log(logits))
    """
    regularization function used is: ||w|| / 2
    """
    regularizationTotal = 0
    for layer in self.layers:
      if isinstance(layer, Layer):
        regularizationTotal = regularizationTotal + np.sum(np.power(layer.w,2))

    output = loss + (self.config['L2_penalty'] / 2) * regularizationTotal
    return output

  def backward_pass(self):
    '''
    implement the backward pass for the whole network.
    hint - use previously built functions.
    '''
    delta = self.targets - self.y
    for layer in reversed(self.layers):     # need to stop at input layer
      delta = layer.backward_pass(delta)


def trainer(model, X_train, y_train, X_valid, y_valid, config):
  """
  Write the code to train the network. Use values from config to set parameters
  such as L2 penalty, number of epochs, momentum, etc.
  """

  batch_size = config['batch_size']
  numEpochs = config['epochs']
  num_train = X_train.shape[0]
  learning_rate = config['learning_rate']

  #getting sample based on batch size
  batch_ind = np.random.choice(num_train, batch_size)
  X_batch = X_train[batch_ind]
  y_batch = y_train[batch_ind]

  training_accuracy = []
  validation_accuracy = []

  count = 0
  validation_error = float("inf")
  best_model = model.layers
  best_found = False
  best_epoch = 0
  
  for i in range(numEpochs):
    print("Current Epoch: ", i + 1)
    for sample in range(batch_size):
      #forwards pass & backpass
      model.forward_pass(X_batch[sample].reshape(1,784), y_batch[sample])[0]
      model.backward_pass()

      for layer in model.layers:
        if isinstance(layer, Layer):

          #checks if we apply momentum
          if (config['momentum'] == False):
            #updating weights
            layer.w = layer.w + learning_rate * layer.d_w
            layer.b = layer.b + learning_rate * layer.d_b
          else:
            if (layer.count > 1):
              layer.w = layer.w + learning_rate * layer.d_w + layer.momentum_d_w
              layer.b = layer.b + learning_rate * layer.d_b + layer.momentum_d_b
            else:
              layer.w = layer.w + learning_rate * layer.d_w
              layer.b = layer.b + learning_rate * layer.d_b

    old_validation_error = validation_error
    validation_error = cross_entropy(model, X_valid, y_valid, model.config['L2_penalty'])

    #compares change of error on validation set
    if (validation_error > old_validation_error):
      count = count + 1
    else:
      count = 0

    #if validation error goes up for multiple epochs, then we assume overfitting
    if (count == config['early_stop_epoch']):
      best_model = copy.deepcopy(model.layers)
      best_epoch = i + 1
      best_found = True

    #adds training and validation set accuracy to list
    training_acc = test(model, X_train, y_train, model.config)
    valid_acc = test(model, X_valid, y_valid, model.config)

    #adding to lists (to be returns by method)
    training_accuracy.append(training_acc)
    validation_accuracy.append(valid_acc)


  if (best_found):
    return training_accuracy, validation_accuracy, best_model, best_epoch
  else:
    return training_accuracy, validation_accuracy, model.layers, numEpochs


def cross_entropy(model, X_set, y_set, regFactor):
  """
  Loss function for softmax regression
  implemented regression based on the function:
  Loss = summation of w_ij ^2
  """
  m = X_set.shape[0]
  model.forward_pass(X_set, y_set)

  p = model.y

  loss = np.sum(-np.log(p) * y_set) / m 

  regularizationTotal = 0
  for layer in model.layers:
    if isinstance(layer, Layer):
      regularizationTotal = regularizationTotal + np.sum(np.power(layer.w,2))

  total_loss = loss + (regFactor / 2) * regularizationTotal

  return total_loss



def test(model, X_test, y_test, config):
  """
  Write code to run the model on the data passed as input and return accuracy.
  """
  numCorrect = 0
  numExamples = X_test.shape[0]
  loss, prediction = model.forward_pass(X_test, y_test)
  for i in range(len(prediction)):
    if (np.argmax(prediction[i]) == np.argmax(y_test[i])):
      numCorrect = numCorrect + 1

  return numCorrect / numExamples


if __name__ == "__main__":
  train_data_fname = 'MNIST_train.pkl'
  valid_data_fname = 'MNIST_valid.pkl'
  test_data_fname = 'MNIST_test.pkl'

  ### Train the network ###
  model = Neuralnetwork(config)
  X_train, y_train = load_data(train_data_fname)
  X_valid, y_valid = load_data(valid_data_fname)
  X_test, y_test = load_data(test_data_fname)
  trainer(model, X_train, y_train, X_valid, y_valid, config)
  test_acc = test(model, X_test, y_test, config)
  print(test_acc)
