# QOSF ADDER CHALLENGE

## Ricky's solution:

Hello, thank you for checking out my Draper adder solution! This problem seemed
to be the most challenging tome and that was the chief reason why I chose it. As a bonus, I've generalized it to find the subset to sum for other lists of integers and outpus, assuming the integers are not negative. 

### Getting Started

Please create a conda environment for the module to run in if you do not have
one: `conda create -n draper python=3.9`

`pip install -r requirements.txt`

Installation You can install from source by cloning this repository and running
a pip install command in the root directory:

```
git clone url = https://github.com/rryoung98/QOSF.git
cd QOSF
python3 -m pip install -e .
```

### Implementation

The problem requires checking all combinations of the list of integers to check
if they sum. The `subset_finder()` defaults to find the subset for the problem
statement, but this implementation has been generalized to take in other
positive integers and outputs.

Here is an example adder circuit for `5+7`.
![circuit](./assets/circuit.png)


#### How it works

The algorithm first converts all the integers to binary and then uses the meet
in the middle strategy to split the list into two and find all the combinations
which add up to the desired value using the draper adder method.

The draper method is implemented using qiskit and applies a QFT without swap
gates then a series of controlled phase gates. 



### Challenges

I faced a decent amount of challenges but all of them were very rewarding. From building the draper circuit to making sure that the python package was successfully deployed this was a pretty fun weekend. I think looking back at the problems I could have implemented this a lot faster if I paid closer attention to the various implementations of the draper circuit from several papers and the Microsoft tutorial. Some of them were for the modulo addition which I spent a good amount of time varifying. Big O considerations were also significant especially since the nature of arithmetic quantum circuit, the running of the circuit, as well as the combinations would slow the draper adder and would be an exciting topic to explore!

### Tests

Some test were made to make sure that functions behave as expected. In the case that the pip install fails the requirements.txt is also available and a demo.

### Conclusion

It was definitely fun doing this project. I'm happy with how relatively robust
the solution and hope that this work can be considered for the mentorship!

Future improvements include running on allowing the ability to run on various
simulators and hardware via kwargs and I would hope to add different methods of
quantum arithmetic

## QOSF PROBLEM 1:

For this problem, you want to find a positive integer that can be composed of
the summation of a subset of the input vector, for example: [1,3,6,4,2], and we
need to find the number 6

the possible solutions are:

- [1,3,2],
- [4,2],
- [6] For this challenge, consider as input a vector of positive integers and a
  positive integer, generate a quantum circuit that indicates with higher
  probability the subset(s) that manage to obtain the number with their sum. Tip
  consider a QRAM to save the input vector and the encoding basis, using the
  before example that could be, we need n qubits for the length of the vector
  and m qubits for the length of the bits. Consider that we will use n = 5
  qubits for the address, so the state |10000⟩ represents the index 1, the state
  |01000⟩ represents the index 2 and so on. And **m = 3**, because the number we
  need is 6 and in binary is 110, so we can use the bases encoding and the state
  result is |110⟩

### In view of the above, the following should be carried out

|index of the vector⟩|value of the index⟩ Consider this format, we need 5 qubits
for the index and 3 qubits of the values, i.e: 1 = > |10000001> 3 = > |01000011>
6 = > |00100110> 4 = > |00010100> 2 = > |00001010> And you want to find 6. The
green part is the index state, and the red is the value. For this example you
need to find an oracle where is the state six in the red qubits is a correct
answer. The output could be

- [1,3,2] = > |11001> ,
- [4,2] = > |00011> ,
- [6] = > |00100> Hint: For this task you can make use of the Adder by Draper, a
  general quantum circuit to make this proposal can be found here, but instead
  of adding 2 numbers find a way to accommodate the request.

Based on the diagram, the QFT and QFT-1 are used and U1 = . Then the values to
be the binary number dep’ends on the U1 gates. Examples of this you can see in
the images, consider the green cat as |0> and purple cat as |1>.

### The challenge

Design a quantum circuit that finds the subsets where the sum is equal to the
value 16 in the following vector [5,7,8,9,1]

### References

Steven A. Cuccaro, Thomas G. Draper, Samuel A. Kutin, David Petrie Moulton
(2004). A new quantum ripple-carry addition circuit.
(https://arxiv.org/abs/quant-ph/0410184)

Thomas G. Draper (2000). Addition on a Quantum Computer
(https://arxiv.org/abs/quant-ph/0008033)
