from .TestProperties import TestProperty, Qarg
from .TestCaseGeneration import TestCaseGenerator
from .TestExecutionEngine import TestExecutor
from .StatisticalAnalysisEngine import StatAnalyser
from math import cos, radians

class QiskitPropertyTest():

    def assertEqual(self, qu0, qu1, qu0_pre = False, qu1_pre = False):

        #Error handling for the parameters
        if not isinstance(qu0, int) or not isinstance(qu1, int) or not isinstance(qu0_pre, bool) or not isinstance(qu1_pre, bool):
            raise Exception(f"Incorrect arguments supplied to assertEqual: qu0: {qu0}, qu1: {qu1}; (Optional: qu0_pre: {qu0_pre}, qu1_pre: {qu1_pre}\nThere should be 2 integers, followed by 2 optional booleans, defaulted to False)")

        generatedTests = [qc.copy() for qc, theta, phi in self.initialisedTests]

        if qu0_pre == qu1_pre:

            #Applies the function to the generated tests only if they are both sampled after running the full program
            if not qu0_pre and not qu1_pre:
                for generatedTest in generatedTests:
                    self.quantumFunction(generatedTest)

            dataFromExec = TestExecutor().runTestsAssertEqual(generatedTests,
                                                              self.testProperty.nbTrials,
                                                              self.testProperty.nbMeasurements,
                                                              qu0,
                                                              qu1,
                                                              self.testProperty.nbClassicalBits,
                                                              self.testProperty.nbClassicalBits + 1)

            testResults = StatAnalyser().testAssertEqual(self.testProperty.p_value, dataFromExec)
            if not qu0_pre and not qu1_pre:
                print(f"AssertEqual({qu0}, {qu1}) results:\n{testResults}\n")
            else:
                print(f"AssertEqual({qu0}_pre, {qu1}_pre) results:\n{testResults}\n")

            return testResults

        else:
            generatedTestsPre = [qc.copy() for qc, theta, phi in self.initialisedTests]

            for generatedTest in generatedTests:
                self.quantumFunction(generatedTest)

            if not qu0_pre:
                dataFrom_qu0 = TestExecutor().runTestsAssertProbability(generatedTests,
                                                                        self.testProperty.nbTrials,
                                                                        self.testProperty.nbMeasurements,
                                                                        qu0,
                                                                        self.testProperty.nbClassicalBits + 1)
            else:
                dataFrom_qu0 = TestExecutor().runTestsAssertProbability(generatedTestsPre,
                                                                        self.testProperty.nbTrials,
                                                                        self.testProperty.nbMeasurements,
                                                                        qu0,
                                                                        self.testProperty.nbClassicalBits + 1)

            if not qu1_pre:
                dataFrom_qu1 = TestExecutor().runTestsAssertProbability(generatedTests,
                                                                        self.testProperty.nbTrials,
                                                                        self.testProperty.nbMeasurements,
                                                                        qu1,
                                                                        self.testProperty.nbClassicalBits + 1)
            else:
                dataFrom_qu1 = TestExecutor().runTestsAssertProbability(generatedTestsPre,
                                                                        self.testProperty.nbTrials,
                                                                        self.testProperty.nbMeasurements,
                                                                        qu1,
                                                                        self.testProperty.nbClassicalBits + 1)


            formattedData = tuple(zip(dataFrom_qu0, dataFrom_qu1))
            testResults = StatAnalyser().testAssertEqual(self.testProperty.p_value, formattedData)

            if not qu0_pre:
                print(f"AssertEqual({qu0}, {qu1}_pre) results:\n{testResults}\n")
            else:
                print(f"AssertEqual({qu0}_pre, {qu1}) results:\n{testResults}\n")

            return testResults



    def assertEntangled(self, qu0, qu1):

        generatedTests = [qc.copy() for qc, theta, phi in self.initialisedTests]

        for generatedTest in generatedTests:
            self.quantumFunction(generatedTest)

        dataFromExec = TestExecutor().runTestsAssertEntangled(generatedTests,
                                                              self.testProperty.nbTrials,
                                                              self.testProperty.nbMeasurements,
                                                              qu0,
                                                              qu1,
                                                              self.testProperty.nbClassicalBits,
                                                              self.testProperty.nbClassicalBits + 1)

        testResults = StatAnalyser().testAssertEntangled(self.testProperty.p_value, dataFromExec)
        print(f"AssertEntangled({qu0}, {qu1}) results:\n{testResults}\n")



    def assertProbability(self, qu0, expectedProba, qu0_pre = False):

        #Error handling
        if not isinstance(qu0, int) or not (isinstance(expectedProba, float) \
           or isinstance(expectedProba, int)) or not isinstance(qu0_pre, bool):
            print(f"qu0: {qu0}, expectedProba: {expectedProba}; (Optional: qu0_pre: {qu0_pre}")
            print(f"There should be an integer, followed by either a float or an int, followed by an optional boolean")
            raise Exception(f"Incorrect arguments supplied to assertProbability")

        expectedProbas = [expectedProba for _ in range(self.testProperty.nbTests)]

        generatedTests = [qc.copy() for qc, theta, phi in self.initialisedTests]

        #Only apply the functions if specified
        if not qu0_pre:
            for generatedTest in generatedTests:
                self.quantumFunction(generatedTest)

        dataFromExec = TestExecutor().runTestsAssertProbability(generatedTests,
                                                                self.testProperty.nbTrials,
                                                                self.testProperty.nbMeasurements,
                                                                qu0,
                                                                self.testProperty.nbClassicalBits + 1)

        testResults = StatAnalyser().testAssertProbability(self.testProperty.p_value, expectedProbas, dataFromExec)

        if not qu0_pre:
            print(f"AssertProbability({qu0}, {expectedProbas[0]}) results:\n{testResults}\n")
        else:
            print(f"AssertProbability({qu0}_pre, {expectedProbas[0]}) results:\n{testResults}\n")




    def assertTeleported(self, sent, received):

        generatedTests = [qc.copy() for qc, theta, phi in self.initialisedTests]

        for generatedTest in generatedTests:
            self.quantumFunction(generatedTest)


        expectedProbas = []
        for qc, thetas, phis in self.initialisedTests:
            expectedProba = cos(radians(thetas[sent]) / 2) ** 2
            expectedProbas.append(expectedProba)

        dataFromReceived = TestExecutor().runTestsAssertProbability(generatedTests,
                                                                    self.testProperty.nbTrials,
                                                                    self.testProperty.nbMeasurements,
                                                                    received,
                                                                    self.testProperty.nbClassicalBits + 1)

        testResults = StatAnalyser().testAssertProbability(self.testProperty.p_value, expectedProbas, dataFromReceived)
        print(f"AssertTeleported({sent}, {received}) results:\n{testResults}\n")



    def runTests(self):
        print(f"Running tests for {type(self).__name__}:\n")

        self.testProperty = self.property()

        self.initialisedTests = TestCaseGenerator().generateTests(self.testProperty)

        self.assertions()

        print(f"Tests for {type(self).__name__} finished\n")
