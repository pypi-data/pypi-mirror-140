from .TestProperties import TestProperty
from .TestCaseGeneration import TestCaseGenerator
from .TestExecutionEngine import TestExecutor
from math import sqrt, acos, asin, sin, degrees, degrees, isclose
from scipy import stats
from qiskit.quantum_info import entanglement_of_formation
import numpy as np

class StatAnalyser:

    #use 2-sample t-test
    #null hypothesis is that the two states are equal
    def testAssertEqual(self,
                        p_value,
                        data):
        testResults = []
        for testIndex in range(len(data)):
            if np.array_equal(data[testIndex][0], data[testIndex][1]):
                testResults.append(True)
                continue

            t, stat_p = stats.ttest_ind(data[testIndex][0], data[testIndex][1])
            testResults.append(p_value <= stat_p)

        return testResults


    def testAssertEntangled(self,
                            p_value,
                            data):
        #print(testResults)
        testResults = []
        for testIndex in range(len(data)):
            totalEntanglement = 0
            for trialResult in data[testIndex]:
                #print(np.sqrt(trialResult))
                totalEntanglement += entanglement_of_formation(np.sqrt(trialResult))
                #print(entanglement_of_formation(np.sqrt(trialResult)))
            totalEntanglement /= len(data[testIndex])
            #print(f"total entanglement: {totalEntanglement}")
            testResults.append(totalEntanglement >= 1 - p_value)

        return testResults



    #Using one-sample t-test
    #The Null hypothesis is that the sample was taken with the same probability as the argument
    #TestResults is a tuple of tuple of bool
    def testAssertProbability(self,
                            p_value: float,
                            expectedProbas,
                            data):

        testResults = []

        for trialIndex in range(len(data)):
            if np.all(data[trialIndex] == data[trialIndex][0]):
                testResults.append(isclose(data[trialIndex][0], expectedProbas[trialIndex], abs_tol=0.01))
                continue

            t, stat_p = stats.ttest_1samp(data[trialIndex], expectedProbas[trialIndex])

            testResults.append(p_value <= stat_p)

            #print(stat_p)

        return testResults



    def testAssertTransformed(self, thetaMin, thetaMax, phiMin, phiMax, testStatevectors):

        results = []
        for statevector in testStatevectors:

            realPart0 = float(statevector[0].real)

            thetaRad = acos(realPart0) * 2

            #print(f"thata degrees from statevector: {degrees(thetaRad)}")

            if sin(thetaRad / 2) == 0:
                raise Exception("Division by 0")

            phiRad1 = acos(float(statevector[1].real) / sin(thetaRad / 2))
            #phiRad2 = asin(float(testStatevector[1].imag) / sin(thetaRad / 2))

            #print(f"values from statevectors: {degrees(thetaRad)}, {degrees(phiRad1)}")

            results.append(degrees(thetaRad) >= thetaMin - 0.001 and degrees(thetaRad) <= thetaMax + 0.001 and \
                           degrees(phiRad1) >= phiMin - 0.001 and degrees(phiRad1) <= phiMax + 0.001)

        return results
