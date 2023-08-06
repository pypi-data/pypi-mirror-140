# Qiskit-PTesting

   This project aims to implement property-based testing for quantum circuits using the qiskit library for Python 3.6 or more.

   To learn more about qiskit, follow this link:
      https://qiskit.org/

   I also recommend following their tutorials on the qiskit library:
      https://qiskit.org/learn/

   To learn more about property-based testing, follow these ressources:
      https://dev.to/jdsteinhauser/intro-to-property-based-testing-2cj8
      https://en.wikipedia.org/wiki/Property\_testing


# Installation (currently work in progress)

   1) Run "pip install qiskit-ptesting"

   2) In any file where you want to use this project, run:
      "from Qiskit_PTesting import QiskitPropertyTest, TestProperty, Qarg"

   That's it, you should be done


# Usage

   1) Create a superclass of "QiskitPropertyTest" using any name you want
   2) In that class, define 3 functions:
      i) property(self)
      ii) quantumFunction(self, qc)
      iii) assertions(self)
   3) Inside of the function "property()", define a TestProperty object and return it
   4) Inside of the function "quantumFunction()", define which steps are needed to be applied to qc (the quantum circuit). All of the generated tests will have those transformations applied.
   5) Inside of the function "assertion()", define which properties you would like to hold true using the built-in assertions.
   6) Run the test class you created using the "runTests()" method.



# How to define a TestProperty

   A TestProperty object contains all of the necessary information to generate random tests.

   It contains:
      1) The p_value for all tests (float between 0 and 1)
      2) The number of randomly generated tests (int greater than 0)
      3) The number of times each generated test will be run, otherwise called the amount of trials (int greater than 0)
      4) The number of times each trial will be measured (int greater than 0)
      5) The amount of required qubits for each test (int greater than 0)
      6) The amount of classical bits required for each test(int greater or equal to 0)
      7) A dictionary of Qarg objects for each qubit that you want to initialise to a specific range/value



# How to initalise a Qarg

   A Qarg object holds 4 ints that define 2 ranges.
   A qubit will use this Qarg to initialise itself to a random value between those 2 ranges.
   Any qubit of a quantum circuit can be initilised using 2 values: a theta and a phi.
   (For those that don't know, the theta corresponds to an angle roughly similar to the "latitude" of the qubit represented as a Bloch Sphere, starting with 0 at the state |0>, and the phi corresponds to its "latitude")
   The first range specifies what values theta can be used to initialise a qubit.
   The second range specifies what values phi can take.



# Assertions

   5 assertions are up to your disposition: (3 currently work properly)

   # assertEqual(qu0, qu1, qu0\_pre = False, qu1\_pre = False)
   This assertion requires 2 arguments, which are the indexes of the qubits to be tested, and 2 optional arguments that specify whether the qubits are to be tested before the quantumFunction() is applied.
   It defaults to False, so if no arguments are specified there, it will compare the qubits after the function is applied.
   This assertion tests whether the probabilities of measuring two qubits in the states |0> or |1> are the same.
   The tests are done on the Z-axis.

   # assertProbability(qu0, expectedProba, qu0\_pre = False)
   This assertion requires 2 arguments: first, the index of the qubit to be tested, and secondly the expected probability of measuring the qubit in the state |0> along the Z-axis.
   It can also optionally take in an extra bool argument, that specifies whether the sampling will occur before the quantumFunction is applied.
   It defaults to False, so the sampling occurs after the function.

   # assertTeleported(sent, received)
   This assertion requires 2 positional arguments:

   # assertEntangled()

   # assertTransformed



# Example (not written yet)





# How it works (not written yet)
