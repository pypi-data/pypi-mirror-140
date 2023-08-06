import math


def checkInputs(problem_labels, weights_ulowa, fuzzyNumbers_ulowa):
    """
    Method that checks if the inputs given by the user are acceptable

    :param fuzzyNumbers_ulowa: a set of fuzzy numbers (4 points each)
    :param weights_ulowa: the weights applied for the specific problem
    :param problem_labels: the vector we want to get the result from
    """
    # Checks the correspondence of the weights and the labels (must have the same length)
    if len(problem_labels) != len(weights_ulowa): raise WeightsError(
        "The input label vector must have the same number of items that the weights' vector")
    # Checks if the boundaries coincide
    i = 0
    while i < 3:
        if fuzzyNumbers_ulowa[i][2] != fuzzyNumbers_ulowa[i + 1][0]: raise FuzzyNumberError(
            "The bounds of the fuzzy set must coincide")
        if fuzzyNumbers_ulowa[i][3] != fuzzyNumbers_ulowa[i + 1][1]: raise FuzzyNumberError(
            "The bounds of the fuzzy set must coincide")
        # Check whether the previous values are smaller than the next values
        for j in range(3):
            if fuzzyNumbers_ulowa[i][j] > fuzzyNumbers_ulowa[i][j + 1]: raise FuzzyNumberError(
                "The previous point must be smaller than the next")
        i = i + 1


def ulowaOperation(problem_labels, weights_ulowa, fuzzyNumbers_ulowa, labels_ulowa):
    """
    Method that computes the ULOWA operation

    :param fuzzyNumbers_ulowa: a set of fuzzy numbers (4 points each)
    :param weights_ulowa: the weights applied for the specific problem
    :param problem_labels: the vector we want to get the result from
    :param labels: an array of the different possible labels
    :return: the result label
    """
    weights_ulowa = weights_ulowa.copy()
    fuzzyNumbers_ulowa = fuzzyNumbers_ulowa.copy()
    labels_ulowa = labels_ulowa.copy()

    # First we check if the inputs given are well-format inputs
    checkInputs(problem_labels, weights_ulowa, fuzzyNumbers_ulowa)
    # Sort the labels
    problem_labels = sort(labels_ulowa, problem_labels)
    # Calculate a and b values
    a = fuzzyNumbers_ulowa[0][0]
    b = fuzzyNumbers_ulowa[len(fuzzyNumbers_ulowa) - 1][3]
    # Start the ULOWA calculation
    if (len(problem_labels) >= 2):
        weight = recalculateWeights(weights_ulowa, len(problem_labels))
        delta = calculateDelta(problem_labels, weight, fuzzyNumbers_ulowa, labels_ulowa)
        deltaList = (delta, delta, delta, delta)
        res = calculateSimilarities(problem_labels, deltaList, labels_ulowa, fuzzyNumbers_ulowa, a, b)
        # Once obtained the result, we remove the last item and substitute with the label (res)
        problem_labels.pop(len(problem_labels) - 1)
        problem_labels[len(problem_labels) - 1] = res
        # We have to recalculate the weights since the result label will carry both previous weights
        aux = weights_ulowa[len(weights_ulowa) - 1]
        weights_ulowa.pop(len(weights_ulowa) - 1)
        weights_ulowa[len(weights_ulowa) - 1] = weights_ulowa[len(weights_ulowa) - 1] + aux
        ulowaOperation(problem_labels, weights_ulowa, fuzzyNumbers_ulowa, labels)
    res = problem_labels[0]
    return res


def calculateSimilarities(problem_labels, deltaList, labels_ulowa, fuzzyNumbers_ulowa, a, b):
    """
    Method that calculates the similarities

    :param labels_ulowa: an array of the different possible labels
    :param fuzzyNumbers_ulowa: a set of fuzzy numbers (4 points each)
    :param a: minimum point of the scale
    :param b: maximum point of the scale
    :param problem_labels: the vector we want to get the result from
    :param deltaList: a vector of four positions with the delta value, delta=(x, x, x, x)
    :return: the label to which the set is more similar
    """

    tag1 = problem_labels[len(problem_labels) - 1]
    tag2 = problem_labels[len(problem_labels) - 2]
    consecutive_var = consecutive(tag1, tag2, labels_ulowa)
    similarities = []
    # If tags are consecutive only 2 similarities must be calculated
    if (consecutive_var == 1):
        sim1 = [similarity(fuzzyNumbers_ulowa[labels_ulowa.index(tag1)], deltaList, a, b), tag1]
        sim2 = [similarity(fuzzyNumbers_ulowa[labels_ulowa.index(tag2)], deltaList, a, b), tag2]
        similarities.append(sim1)
        similarities.append(sim2)
    # If tags aren't consecutive, more similarities must be calculated
    else:
        index = labels_ulowa.index(tag1)
        while tag1 != tag2:
            aux = [similarity(fuzzyNumbers_ulowa[labels_ulowa.index(tag1)], deltaList, a, b), tag1]
            similarities.append(aux)
            index = index + 1
            tag1 = labels_ulowa[index]
    aux = [similarity(fuzzyNumbers_ulowa[labels_ulowa.index(tag1)], deltaList, a, b), tag1]
    similarities.append(aux)
    # Once we have determined the similarities, we look for the highest value, and we return its label
    highest = 0.0
    label = ""
    for i in similarities:
        if i[0] > highest:
            highest = i[0]
            label = i[1]
    return label


def consecutive(tag1, tag2, labels_ulowa):
    """
    Method that calculates whether two tags are consecutive in the reference vector

    :param labels_ulowa: reference label vector
    :param tag1: first tag to analyze
    :param tag2: second tag to analyze
    :return: the number of positions of their distance
    """
    return (abs(labels_ulowa.index(tag1) - labels_ulowa.index(tag2)))


def recalculateWeights(weights_ulowa, length):
    """
    Method that calculates the weights when the set gets smaller

    :param weights_ulowa: the weights applied for the specific problem
    :param length: the length of the problem labels' vector
    :return: the new weight
    """
    denominator = (weights_ulowa[length - 2] + weights_ulowa[length - 1])
    if denominator == 0.0:
        return 0.0
    else:
        return (weights_ulowa[length - 2] / denominator)


def calculateDelta(problem_labels, weight, fuzzyNumbers_ulowa, labels_ulowa):
    """
    Method that calculates delta value as a 4-component vector
    Delta = (x, x, x, x)

    :param labels_ulowa: an array of the different possible labels
    :param problem_labels: the vector we want to get the result from
    :param weight: the weights applied for the specific problem
    :param fuzzyNumbers_ulowa: a set of fuzzy numbers (4 points each)
    :return: the value of delta as a 4-component vector
    """
    xsi = getCOG(fuzzyNumbers_ulowa[labels_ulowa.index(problem_labels[len(problem_labels) - 1])])
    xsj = getCOG(fuzzyNumbers_ulowa[labels_ulowa.index(problem_labels[len(problem_labels) - 2])])
    return (xsi + weight * (xsj - xsi))


def getCOG(fuzzyN):
    """
    Method that calculates the centre of gravity of a fuzzy set (COG)

    :param fuzzyN: a fuzzy set given with 4 points, F = (a1, a2, a3, a4)
    :return: the x value of COG
    """
    # function that searches the centre of gravity (COG) of a fuzzy number
    if fuzzyN[0] == fuzzyN[3]:
        y = 0.5
    else:
        y = (1 / 6) * ((fuzzyN[2] - fuzzyN[1]) / (fuzzyN[3] - fuzzyN[0]) + 2)
    x = (y * (fuzzyN[2] + fuzzyN[1]) + (fuzzyN[3] + fuzzyN[0]) * (1 - y)) / 2

    return x


def specificity(fuzzyN, a, b):
    """
    Method that calculates the specificity of a given fuzzy number

    :param fuzzyN: the fuzzy set we want to get the specificity from
    :return the specificity
    """
    area = ((fuzzyN[3] - fuzzyN[0]) + (fuzzyN[2] - fuzzyN[1])) / 2
    res = area / (b - a)
    res = 1 - res
    return res


def fuzziness(fuzzyN, a, b):
    """
    Method that calculates the fuzziness of a given fuzzy number

    :param fuzzyN: the fuzzy set we want to get the fuzziness from
    :return the fuzziness
    """
    area1 = (fuzzyN[1] - fuzzyN[0]) / 2
    area2 = (fuzzyN[3] - fuzzyN[2]) / 2
    res = area1 + area2
    res = res * (1 / (b - a))
    return res


def getCOM(fuzzyN):
    """
    Method that finds out the COM value for a fuzzy set

    :param fuzzyN: the fuzzy set we want to calculate the COM from
    :return: its COM value (Center of Maximum)
    """
    return (fuzzyN[1] + fuzzyN[2]) / 2


def getOrdinal(scale, tag):
    """
    Method that calculates the ordinal value of a given tag
    :param scale: the reference tags scale
    :param tag: the tag we want to get the result from
    :return: its ordinal value
    """
    return scale.index(tag) + 1


def similarity(fuzzSet1, fuzzSet2, a, b):
    """
    Method that calculates the similarity between two fuzzy sets

    :param a: minimum point of the scale
    :param b: maximum point of the scale
    :param fuzzSet1: the first fuzzy set, F1 = (a1, a2, a3, a4)
    :param fuzzSet2: the second fuzzy set, F2 = (b1, b2, b3, b4)
    :return: the similarity between the two fuzzy sets
    """
    # function that calculates the similarity between two fuzzy numbers
    res = []
    for i in range(0, 4):
        res.append(2 - abs((fuzzSet1[i] / (b - a)) - (fuzzSet2[i] / (b - a))))
    # res = math.prod(res)
    result = 1.0
    for i in res:
        result = result * i
    res = result ** (1 / 4) - 1
    return res


def sort(reference, scale):
    """
    Method that sorts the problem labels based on the position of the reference scale

    :param reference: the reference labelled scale
    :param scale: the problem labels' vector
    :return: the problem labels' vector once sorted
    """
    # function that sorts the scale vector from best to worst, based on a reference scale vector introduced by the user
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(scale) - 1):
            index1 = reference.index(scale[i])
            index2 = reference.index(scale[i + 1])
            if index1 < index2:
                aux = scale[i + 1]
                scale[i + 1] = scale[i]
                scale[i] = aux
                swapped = True
    return scale


class FuzzyNumberError(Exception):
    # error in case an introduced point for a given fuzzy set is smaller than the previous one or the boundaries does
    # not match
    pass


class WeightsError(Exception):
    # error in case the length of the weights' vector doesn't match the length of the problem labels vector
    pass


############################################
##  THIS IS A SECTION FOR INPUT, IN CASE  ##
##    THE USER WANTS TO INTRODUCE DATA    ##
##       THROUGH THE COMMAND LINE         ##
############################################


def inputFuzzySets(scale):
    # function that asks the user to introduce the fuzzy sets with its four numbers
    a = []
    phrases = ["first", "second", "third", "fourth"]
    for i in scale:
        print(f"You are about to introduce the fuzzy set for {i}")
        list = []
        if (scale.index(i) == 0):
            for i in range(0, 4):
                list.append(float(input(f"Introduce {phrases[i]} point")))
                if (i >= 1):
                    if (list[i] < list[i - 1]):
                        raise FuzzyNumberError("The next value has to be greater than the previous!")
        else:
            list.append(a[scale.index(i) - 1][2])
            list.append(a[scale.index(i) - 1][3])
            for i in range(2, 4):
                list.append(float(input(f"Introduce {phrases[i]} point")))
                if (i >= 1):
                    if (list[i] < list[i - 1]):
                        raise FuzzyNumberError("The next value has to be greater than the previous!")
        a.append(list)
        print(a)
    print(f"Your fuzzy sets are: {a}")
    print("Is it okay? Type YES. If not, type NO")
    answer = input()
    if answer == "NO" or answer == "no":
        inputFuzzySets(scale)
    return a


def inputScale():
    # function that asks the user to introduce the scale (e.g: VL, L, M, H, VH)
    scale = []
    phrases = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth", "tenth"]
    number = int(input("How many tags will you be defining?"))
    print("Remember that you must introduce the scale from worst to best")
    for i in range(0, number):
        scale.append(input(f"Introduce the {phrases[i]} scale"))
    print("Your scale set is: " + str(scale))
    answer = input("Is it okay? Type YES. If not, type NO")
    if answer == "NO" or answer == "no":
        inputScale()
    return scale


def inputWeights(length):
    # function that asks the user to introduce the weights' vector.
    # it receives a parameter lenght so that it matches the scale's vector lenght
    weights = []
    phrases = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "nineth", "tenth"]
    print("Remember that you must introduce the weights according to the position on the scale")
    for i in range(length):
        weights.append(float(input(f"Introduce the {phrases[i]} weight")))
    if sum(weights) > 1 or sum(weights) < 1:
        raise WeightsError("Weights must add up to 1")
    print("Your weights set is: " + str(weights))
    answer = input("Is it okay? Type YES. If not, type NO")
    if answer == "NO" or answer == "no":
        inputWeights(length)
    return weights


def inputData():
    scale = inputScale()
    fuzzSet = inputFuzzySets(scale)
    weights = inputWeights(len(scale))
    return (scale, fuzzSet, weights)


fuzzyNumbers = [[0.0, 0.0, 0.0, 2.0], [0.0, 2.0, 2.0, 5.0], [2.0, 5.0, 5.0, 6.0], [5.0, 6.0, 6.0, 7.0],
                [6.0, 7.0, 8.0, 9.0], [8.0, 9.0, 9.0, 10.0], [9.0, 10.0, 10.0, 10.0]]

labels = ["VL", "L", "M", "AH", "H", "VH", "P"]

weights = [0.0, 0.0, 0.5, 0.5, 0.0]

performance_table = [["VL", "VL", "P", "H", "VL"], ["VL", "VL", "H", "P", "P"], ["VL", "VL", "L", "M", "L"],
                     ["VH", "L", "H", "H", "AH"], ["P", "L", "H", "L", "AH"]]

results = []
for alternative in performance_table:
    results.append(ulowaOperation(alternative, weights, fuzzyNumbers, labels))

print(results)
