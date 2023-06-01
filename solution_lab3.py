import sys
import math

class Node:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, x, subtrees):
        self.x = x
        self.subtrees = subtrees

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.subtrees})"

class ID3:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, D, D_parent, X):
        self.D = D
        self.D_parent = D_parent
        self.X = X[:-1]
        self.branches = []
        self.node = ""
    
    def fit(self, train_list, depth):
        feature_dict = makeFeatureDict(self.D[:], self.X[:])
        self.node = ID3Algorithm(self.D[:], self.D_parent[:], self.X[:], train_list, feature_dict, depth, 1)
        print('[BRANCHES]:')
        self.branches = buildBranches(self.node, 1, [])
        for branch in self.branches:
            print(branch)

    def predict(self, test_list):
        predictions = ''
        new_test_list = checkTestList(test_list)
        for test in new_test_list[1:]:
            prediction = testExample(test, new_test_list[0], self.node, new_test_list)
            predictions += prediction + ' '
        print('[PREDICTIONS]: ' + predictions[:-1])
        evaluate(test_list, predictions[:-1])
        return


def evaluate(test_list, predictions):
    matrix = {}
    labels = set()
    correct = 0
    total = len(test_list) - 1
    for i in range(len(test_list[1:])):
        prediction = predictions.split(' ')[i]
        real = test_list[i+1].split(',')[-1]
        if prediction == real: correct += 1
        key = prediction + " " + real
        labels.add(prediction)
        labels.add(real)
        matrix[key] = matrix.get(key,0) + 1
    print('[ACCURACY]: %.5f' % (round(correct / total, 5)))
    print('[CONFUSION_MATRIX]:')
    for real in sorted(labels):
        string = ''
        for predicted in sorted(labels):
            string += str(matrix.get(predicted + ' ' + real,0)) + ' '
        print(string[:-1])

def testExample(test, test_list, node, test_list_all):
    test_dict = dict()
    test_list = test_list.split(',')
    test = test.split(',')
    if type(node) == str: return node
    for i in range(len(test_list)):
        test_dict[test_list[i]] = test[i] 
    while True:
        if type(node) == str: return node
        feature = node.x
        if feature in test_list:
            test_feature = test_dict[feature]
            for subtree in node.subtrees:
                if subtree[0] == test_feature:
                    if type(subtree[1]) == str: return subtree[1]
                    else:
                        node = subtree[1]
                    break
        else:
            labels = []
            for t in test_list_all[1:]:
                t = t.split(',')
                labels.append(t[-1])
            node = sorted(labels)[0]
        
def checkTestList(test_list):
    i = 0
    feature_to_remove = 0
    value_to_remove = 0
    while i <= len(test_list[0].split(','))-1:
        value_set = set()
        for test in test_list[1:]:
            test = test.split(',')
            value_set.add(test[i])
        if len(value_set) == 1:
            feature_to_remove = test_list[0].split(',')[i]
            value_to_remove = test[i]
        i+=1
    if value_to_remove == 0 and feature_to_remove == 0:
        return test_list
    new_test_list = []
    for row in test_list:
        test_row = []
        row = row.split(',')
        for r in row:
            if r != feature_to_remove and r != value_to_remove:
                test_row.append(r)
        test_row = ",".join(test_row)
        new_test_list.append(test_row)
    return new_test_list

def buildBranches(node, level, branches):
    if type(node) == str:
        return([node])
    else:
        for subtree in node.subtrees:
            current_branch = str(level) + ':' + str(node.x) + '=' + subtree[0] + ''
            subbranches = buildBranches(subtree[1], level+1, [])
            for subbranch in subbranches:
                branches.append(current_branch + ' ' + subbranch)
        return branches

def ID3Algorithm(D, D_parent, X, input_list, feature_dict, depth, current_depth):
    if current_depth <= depth:
        if D == []:
            v = argmaxLabel(D_parent)
            return v
        v = argmaxLabel(D)
        if X == [] or containsOneLabel(D, v):
            return v
        x = argmaxIG(D, X, feature_dict)
        subtrees = []
        feature_set = feature_dict[x][1]
        feature_index = feature_dict[x][0]
        X.remove(x)
        del feature_dict[x]
        for v in feature_set:
            D_new = getNewD(D, v, feature_index)
            t = ID3Algorithm(D_new, D[:], X[:], input_list, feature_dict.copy(), depth, current_depth+1)
            subtrees.append((v, t))
        return Node(x, subtrees)
    else:
        if D == []:
            return argmaxLabel(D_parent)
        v = argmaxLabel(D)
        return v

def getNewD(D, v, feature_index):
    new_D = []
    for row in D:
        values = row.split(',')
        if v == values[feature_index]:
            new_D.append(row)
    return new_D

def countEntropyAndSingleIG(D, x, feature_index):
    leaves = leafValue(D, x, feature_index)
    if leaves == dict(): return 0
    total = 0
    for leaf in leaves.keys():
        total += leaves[leaf]
    entropy = 0
    for leaf in leaves.keys():
        if leaves[leaf] != 0:
            entropy -= (leaves[leaf]/total) * math.log((leaves[leaf]/total),2)
    ig = total / len(D) * entropy
    return ig

def getIG(feature, values, entropy_D, D, feature_index):
    ig = entropy_D
    for x in values:
        feature_ig = countEntropyAndSingleIG(D, x, feature_index)
        ig -= feature_ig
    return ig

def argmaxIG(D, X, feature_dict):
    label_num = labelNumber(D)
    total = len(D)
    entropy_D = 0
    for label in label_num:
        if label_num[label] != 0:
            entropy_D -= (label_num[label]/total) * math.log((label_num[label]/total),2)
    ig_dict = dict()
    for feature in feature_dict.keys():
        ig = getIG(feature, feature_dict[feature][1], entropy_D, D, feature_dict[feature][0])
        ig_dict[feature] = ig
    max_value = max(ig_dict.values())
    max_key = sorted([k for k, v in ig_dict.items() if v == max_value])[0]
    return max_key

def containsOneLabel(D, v):
    labels = set()
    for x in D:
        x = x.split(',')
        labels.add(x[-1])
    if len(labels) == 1 and v in labels:
        return True
    else: return False

def leafValue(D, value, feature_index):
    leaves = dict()
    for x in D:
        x = x.split(',')
        if value == x[feature_index]:
            leaves[x[-1]] = leaves.get(x[-1], 0) + 1
    return leaves

def labelNumber(D):
    label_num = dict()
    for x in D:
        x = x.split(',')
        label_num[x[-1]] = label_num.get(x[-1], 0) + 1
    return label_num

def argmaxLabel(D):
    label_num = labelNumber(D)
    max_value = max(label_num.values())
    max_key = sorted([k for k, v in label_num.items() if v == max_value])[0]
    return(max_key)

def makeFeatureDict(D, X):
    featureDict = dict()
    i = 0
    for x in X:
        features = set()
        for d in D:
            d = d.split(',')
            features.add(d[i])
        featureDict[x] = (X.index(x), features)
        i += 1
    return featureDict

def readData(train_dataset, test_dataset):
    with open(train_dataset, 'r', encoding='UTF-8') as train:
        train_list = train.read().strip().splitlines()
    with open(test_dataset, 'r', encoding='UTF-8') as test:
        test_list = test.read().strip().splitlines()
    return train_list, test_list

if len(sys.argv) == 4:
    if sys.argv[3].isnumeric():
        depth = sys.argv[3]
        train_dataset = sys.argv[1]
        test_dataset = sys.argv[2]
        train_list, test_list = readData(train_dataset, test_dataset)
        X = train_list[0].split(',')
        D = train_list[1:]

        model = ID3(D, D, X) #construct model instance 
        model.fit(train_list, float(depth)) #learn the model 
        predictions = model.predict(test_list) #generate predictions on unseen data
    else:
        print('Last argument must be numeric.')
elif len(sys.argv) == 3:
    train_dataset = sys.argv[1]
    test_dataset = sys.argv[2]
    train_list, test_list = readData(train_dataset, test_dataset)
    X = train_list[0].split(',')
    D = train_list[1:]

    model = ID3(D, D, X) #construct model instance 
    model.fit(train_list, float(math.inf)) #learn the model 
    predictions = model.predict(test_list) #generate predictions on unseen data
else:
    print('Wrong number of arguments.')