## ULOWA MODULE 
Please, read carefully before using this library.

This module has been made for academic purposes. If you want to use it, cite the author.

### 1. Installation
First, you can simpy install it by using the pip comand: `pip install ulowa`
### 2. Usage
#### 2.1. ULOWA
It is necessary to define a **fuzzy set**, each one with 4 points, e.g:
`fuzzyNumbers = [[0.0, 0.0, 1.0, 2.0], [1.0, 2.0, 4.0, 5.0], [4.0, 5.0, 5.0, 6.0], [5.0, 6.0, 6.0, 7.0],
                [6.0, 7.0, 8.0, 8.5], [8.0, 8.5, 9.0, 9.5], [9.0, 9.5, 10.0, 10.0]]`

*Note that the scale may vary, it isn't compulsory to be from 0 to 10*

Then, you must define the weights and the labels for the scale, e.g:
`weights = [0.6, 0.2, 0.2, 0.0, 0.0]`
`labels = ["VL", "L", "M", "AH", "H", "VH", "P"]`

*Note that the weights must sum up to 1, and the scale must be ordered from worst to best tag.*

Now, we should define the labels for our specific problem, e.g:
`problem_labels = ["VL", "VL", "L", "M", "L"]`

Eventually, we call the ULOWA function:
`ulowaOperation(problem_labels, weights, fuzzyNumbers, labels)`

In case you need to analyze more alternatives, you may need to establish a performance table e.g: `performance_table` in which you will include several problem labels, such as:
`performance_table = [["VL", "VL", "P", "H", "VL"], ["VL", "VL", "H", "P", "P"], ["VL", "VL", "L", "M", "L"],
                     ["VH", "L", "H", "H", "AH"], ["P", "L", "H", "L", "AH"]]`

*Note that the tags doesn't need to be sorted, since a specific method will do so.*

Now, in order to get a table with all the results, you should execute a code like the following:
```
performance_table = [["VL", "VL", "P", "H", "VL"], ["VL", "VL", "H", "P", "P"], ["VL", "VL", "L", "M", "L"],
                     ["VH", "L", "H", "H", "AH"], ["P", "L", "H", "L", "AH"]]
results = []
for alternative in performance_table:
    results.append(ulowaOperation(alternative, weights, fuzzyNumbers, labels))
print(results)

```
#### 2.2. Specificity and Fuzziness
This module also allows you to calculate the specificity and fuzziness of a given fuzzy set.
In this case, a code like the shown below must be executed:
```
a = fuzzyNumbers[0][0]
b = fuzzyNumbers[len(fuzzyNumbers) - 1][3]
order=1
for i in fuzzyNumbers:
    print(f"\nThe specificity of the {order} fuzzy set is: {specificity(i, a, b)}")
    print(f"\nThe fuzziness of the {order} fuzzy set is: {fuzziness(i, a, b)}")
    order = order + 1
```
#### 2.3. Defuzzification
There are three methods that can be used in this package: `getCOG(fuzzyNumber)`, `getOrdinal(scale, tag)` and `getCOM(fuzzyNumber)`.
Here is an example code of their usage:
```
fuzzyNumbers = [[0.0, 0.0, 1.0, 2.0], [1.0, 2.0, 4.0, 5.0], [4.0, 5.0, 5.0, 6.0], [5.0, 6.0, 6.0, 7.0],
                [6.0, 7.0, 8.0, 8.5], [8.0, 8.5, 9.0, 9.5], [9.0, 9.5, 10.0, 10.0]]
                
print(f"The center of gravity of the first fuzzy set is: {getCOG(fuzzyNumbers[0])}")
print(f"The center of maximum of the first fuzzy set is: {getCOM(fuzzyNumbers[0])}")

# Those will give us the COG and COM of the first fuzzy number

labels = ["VL", "L", "M", "AH", "H", "VH", "P"]
tag = "VL"
print(f"The ordinal value for tag {tag} is {getOrdinal(labels, tag)}")

```
*The code shown above can be done in a loop so that we can get for example the ordinal values for all the results of the ULOWA operation.*

**Author:** Ignacio Miguel Rodríguez - [ITAKA research group](https://deim.urv.cat/~itaka/itaka2/index.html) (URV)

**Contact:** [Send e-mail](mailto:ignacio.miguel@urv.cat)