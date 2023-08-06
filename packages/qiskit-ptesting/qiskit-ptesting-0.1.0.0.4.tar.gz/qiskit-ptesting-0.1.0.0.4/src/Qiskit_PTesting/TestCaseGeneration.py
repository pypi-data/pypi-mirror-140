from qiskit.circuit.quantumcircuit import QuantumCircuit
from .TestProperties import Qarg, TestProperty
import random
from math import pi, cos, sin, sqrt, radians, degrees
import cmath
import numpy as np

class TestCaseGenerator:

    #Returns a tuple containing a QuantumCircuit, a list of the thetas used to initialise the qc and the phis used
    def generateTest(self, testProperties: TestProperty):

        qargs = testProperties.preconditions_q
        #cargs = testProperties.preconditions_c
        #TODO do cargs or remove?

        #Adds 2 classical bits to read the results of any assertion
        #Those bits will not interfere with the normal functioning of the program
        qc = QuantumCircuit(testProperties.nbQubits, testProperties.nbClassicalBits + 2)

        theta_init = []
        phi_init = []

        for key, value in qargs.items():
            #converts from degrees to radian
            randomTheta_deg = random.randint(value.minTheta, value.maxTheta)
            randomPhi_deg = random.randint(value.minPhi, value.maxPhi)

            theta_init.append(randomTheta_deg)
            phi_init.append(randomPhi_deg)

            randomTheta = radians(randomTheta_deg)
            randomPhi = radians(randomPhi_deg)

            value0 = cos(randomTheta/2)
            value1 = cmath.exp(randomPhi * 1j) * sin(randomTheta / 2)

            #print(f"values initialised: {degrees(randomTheta)}, {degrees(randomPhi)}")

            qc.initialize([value0, value1], key)

        return (qc, theta_init, phi_init)

    def generateTests(self, testProperties: TestProperty):
        return [self.generateTest(testProperties) for _ in range(testProperties.nbTests)]

