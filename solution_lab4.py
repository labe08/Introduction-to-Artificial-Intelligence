import sys
import argparse
import math
import re
import operator
import numpy as np

class Neuron:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, bias, weights):
        self.bias = bias
        self.weights = weights

    def __repr__(self) -> str:
        return f"{type(self).__name__}(w={self.weights}, b={self.bias})"

    def calculateOutputNeuron(self, input_vector):
        sum = 0
        for i in range(len(self.weights)):
            num = float(self.weights[i]) * float(input_vector[i])
            sum += num
        net = sum + float(self.bias) 
        y = 1/(1 + np.exp(-net))
        return y

class Neural_Network:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, neuron_layers, weights_final, bias_final):
        self.neuron_layers = neuron_layers
        self.weights_final = weights_final
        self.bias_final = bias_final

    def __repr__(self) -> str:
        return f"{type(self).__name__}(neurons={self.neuron_layers})"

    def calculateOutputNN(self, input_vector):
        last = self.neuron_layers[list(self.neuron_layers.keys())[-1]]
        for layer in self.neuron_layers.values():
            outputs = []
            for neuron in layer:
                y = neuron.calculateOutputNeuron(input_vector)
                outputs.append(y)
            if layer == last:
                sum = 0
                for i in range(len(self.weights_final)):
                    num = float(self.weights_final[i]) * float(outputs[i])
                    sum += num
                output_final = sum + float(self.bias_final)
                return output_final 
            input_vector = outputs

    def meanSquaredError(self, y_set, output_set):
        sum = 0
        for i in range(len(y_set)):
            subtraction = float(y_set[i]) - float(output_set[i])
            err_single = math.pow(subtraction, 2)
            sum += err_single
        N = len(y_set)
        err = 1/N * sum
        return err

def loadData(train_set, test_set):
    with open(train_set, 'r', encoding='UTF-8') as train:
        train_list = train.read().strip().splitlines()
    with open(test_set, 'r', encoding='UTF-8') as test:
        test_list = test.read().strip().splitlines()
    return train_list, test_list

def defineNN(nn, train):
    train = train.split(',')[:-1]
    nn_layers = [int(s) for s in re.findall(r'\d+', nn)]
    neuron_layers = dict()
    i = 1
    weights_final = []
    for n in range(nn_layers[-1]):
        weight = np.random.normal(loc=0,scale=0.01)
        weights_final.append(weight)
    bias_final = np.random.normal(loc=0,scale=0.01)
    for layer in nn_layers:
        neurons = []
        for n in range(layer):
            weights = []
            for x in range(len(train)):
                weight = np.random.normal(loc=0,scale=0.01)
                weights.append(weight)
            bias = np.random.normal(loc=0,scale=0.01)
            neuron = Neuron(bias, weights)
            neurons.append(neuron)
        neuron_layers[i] = neurons
        i += 1
    return neuron_layers, weights_final, bias_final

def mutate(mean, p):
    rand_num = np.random.uniform(0, 1)
    if rand_num < p:
        mutation_weight = np.random.normal(loc=0,scale=float(args['K']))
        mean += mutation_weight
    return mean

def crossoverAndMutation(neuraln1, neuraln2, p):
    #calculate final weights and bias
    new_weights_final = []
    for i in range(len(neuraln1.weights_final)):
        mean = (neuraln1.weights_final[i] + neuraln2.weights_final[i]) / 2
        new_weight = mutate(mean, p)
        new_weights_final.append(new_weight)
    new_bias_final = (neuraln1.bias_final + neuraln2.bias_final) / 2
    new_bias_final = mutate(new_bias_final, p)
    #calculate new weights and biases for each neuron and add new neurons
    new_biases = []
    neural_network_list = list(neuraln1.neuron_layers.values())
    neural_network_list2 = list(neuraln2.neuron_layers.values())
    neuron_layers = dict()
    for i in range(len(neural_network_list)):
        neurons = []
        for j in range(len(neural_network_list[i])):
            new_weights = []
            for k in range(len(neural_network_list[i][j].weights)):
                mean = (neural_network_list[i][j].weights[k] + neural_network_list2[i][j].weights[k]) / 2
                new_weight = mutate(mean, p)
                new_weights.append(new_weight)
            mean_bias = (neural_network_list[i][j].bias + neural_network_list2[i][j].bias) / 2
            new_bias = mutate(mean_bias, p)
            neuron = Neuron(new_bias, new_weights)
            neurons.append(neuron)
        neuron_layers[i+1] = neurons
    neural_network = Neural_Network(neuron_layers, new_weights_final, new_bias_final)
    return neural_network
                    
def crossover(fitness_total, sorted_network_dict, p):
    num1 = np.random.uniform(0, 1)
    neuraln1 = None
    neuraln2 = None
    sum = 0
    for n in sorted_network_dict.keys():
        proportion = sorted_network_dict[n] / fitness_total
        sum += proportion
        if sum > num1:
            neuraln1 = n
            break
    found = False
    while not found:
        num2 = np.random.uniform(0, 1)
        sum = 0
        for n in sorted_network_dict.keys():
            proportion = sorted_network_dict[n] / fitness_total
            sum += proportion
            if sum > num2:
                if n != neuraln1:
                    neuraln2 = n
                    found = True
                    break
                else: break
    new_network = crossoverAndMutation(neuraln1, neuraln2, p)
    return new_network

#main
if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', required=True)
    parser.add_argument('--test', required=True)
    parser.add_argument('--nn', required=True)
    parser.add_argument('--popsize', required=True)
    parser.add_argument('--elitism', required=True)
    parser.add_argument('--p', required=True)
    parser.add_argument('--K', required=True)
    parser.add_argument('--iter', required=True)
    args = vars(parser.parse_args())
   
    train, test = loadData(args['train'], args['test'])
    iteration = 1
    networks = []

    for i in range(int(args['popsize'])):
        #initialize neural networks
        neuron_layers, weights_final, bias_final = defineNN(args['nn'], train[0])
        neural_network = Neural_Network(neuron_layers, weights_final, bias_final)
        networks.append(neural_network)

    fittest = None
    #iterate generations and calculate train error
    while iteration <= int(args['iter'])+1:
        network_dict = dict()
        for network in networks:
            y_set = []
            output_set = []
            for example in train[1:]:
                example = example.split(',')
                x_vector = example[:-1]
                y = example[-1]
                y_set.append(y)
                output = network.calculateOutputNN(x_vector)
                output_set.append(output)
            error = network.meanSquaredError(y_set, output_set)
            network_dict[network] = 1/error

        sorted_network_dict = dict(sorted(network_dict.items(), key=operator.itemgetter(1),reverse=True))        
        #print error for best chromosome on train set
        if iteration % 2000 == 0:
            print('[Train error @' + str(iteration) + ']: ' + str(1/list(sorted_network_dict.values())[0]))
        #fitness and new population
        fitness_total = sum(sorted_network_dict.values())
        networks_new = []
        sorted_network_list = list(sorted_network_dict.keys())
        #if last iteration get the fittest network
        if iteration == int(args['iter'])+1:
            fittest = sorted_network_list[0]
            break
        #elitism, crossover and mutation
        for i in range(int(args['elitism'])):
            networks_new.append(sorted_network_list[i])
        while len(networks_new) < int(args['popsize']):
            new_network = crossover(fitness_total, sorted_network_dict, float(args['p']))
            networks_new.append(new_network)  

        networks = networks_new
        iteration += 1

    #test the fittest network
    y_set = []
    output_set = []
    for example in test[1:]:
        example = example.split(',')
        x_vector = example[:-1]
        y = example[-1]
        y_set.append(y)
        output = fittest.calculateOutputNN(x_vector)
        output_set.append(output)
    error = network.meanSquaredError(y_set, output_set)
    print('[Test error]: ' + str(error))

else:
    print('Not enough arguments!')