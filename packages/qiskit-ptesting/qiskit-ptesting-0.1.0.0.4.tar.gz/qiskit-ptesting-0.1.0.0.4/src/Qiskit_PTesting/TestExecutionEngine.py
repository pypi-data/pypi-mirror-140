from qiskit import Aer, QuantumCircuit
import numpy as np

class TestExecutor:

    def runTestAssertEqual(self,
                           qc,
                           nbTrials,
                           nbMeasurements,
                           qu0,
                           qu1,
                           measuredBit0,
                           measuredBit1):

        sim = Aer.get_backend('aer_simulator')

        qc.measure(qu0, measuredBit0)
        qc.measure(qu1, measuredBit1)

        #print(qc)
        #qc.draw(output="mpl")
        #plt.show()

        trialProbas0 = np.empty(nbTrials)
        trialProbas1 = np.empty(nbTrials)

        for trialIndex in range(nbTrials):
            result = sim.run(qc, shots = nbMeasurements).result()
            counts = result.get_counts()
            #print(counts)
            #counts the results for each qubit
            nb0s_qu0 = nb0s_qu1 = 0
            for elem in counts:
                if elem[::-1][measuredBit0] == '0': nb0s_qu0 += counts[elem]
                if elem[::-1][measuredBit1] == '0': nb0s_qu1 += counts[elem]


            trialProba0 = nb0s_qu0 / nbMeasurements
            trialProba1 = nb0s_qu1 / nbMeasurements

            #print(trialproba0)
            #print(f"{nb0s_qu0}, {nbmeasurements - nb0s_qu1}")

            trialProbas0[trialIndex] = trialProba0
            trialProbas1[trialIndex] = trialProba1
        #print(trialprobas0)
        return (trialProbas0, trialProbas1)

    #Returns a list of list of tuple of tuple of int
    def runTestsAssertEqual(self,
                            initialisedTests,
                            nbTrials,
                            nbMeasurements,
                            qu0,
                            qu1,
                            measuredBit0,
                            measuredBit1):
        retList = []
        for qc in initialisedTests:
            retList.append(self.runTestAssertEqual(qc, nbTrials, nbMeasurements, qu0, qu1, measuredBit0, measuredBit1))
        return retList


    #Return for each test the recreated "statevector" of 2 bits
    def runTestAssertEntangled(self,
                               qc,
                               nbTrials,
                               nbMeasurements,
                               qu0,
                               qu1,
                               measuredBit0,
                               measuredBit1):

        sim = Aer.get_backend('aer_simulator')

        qc.measure(qu0, measuredBit0)
        qc.measure(qu1, measuredBit1)

        #print(qc)
        #qc.draw(output="mpl")
        #plt.show()

        trialVectors = np.zeros((nbTrials, 4))

        for trialIndex in range(nbTrials):
            result = sim.run(qc, shots = nbMeasurements).result()
            counts = result.get_counts()
            #print(counts)

            for key, value in counts.items():
                #Has to be reversed before
                if key[0:2] == "00":
                    trialVectors[trialIndex][0] = value / nbMeasurements
                elif key[0:2] == "10":
                    trialVectors[trialIndex][1] = value / nbMeasurements
                elif key[0:2] == "01":
                    trialVectors[trialIndex][2] = value / nbMeasurements
                elif key[0:2] == "11":
                    trialVectors[trialIndex][3] = value / nbMeasurements

        #print(trialVectors)
        return trialVectors



    def runTestsAssertEntangled(self,
                                initialisedTests,
                                nbTrials,
                                nbMeasurements,
                                qu0,
                                qu1,
                                measuredBit0,
                                measuredBit1):
        retList = []
        for qc in initialisedTests:
            retList.append(self.runTestAssertEntangled(qc, nbTrials, nbMeasurements, qu0, qu1, measuredBit0, measuredBit1))
        return retList


    def runTestAssertProbability(self,
                                 qc,
                                 nbTrials,
                                 nbMeasurements,
                                 qu0,
                                 measuredBit):

        sim = Aer.get_backend('aer_simulator')

        qc.measure(qu0, measuredBit)

        #print(qc)

        trialProbas = np.empty(nbTrials)

        for trialIndex in range(nbTrials):
            result = sim.run(qc, shots = nbMeasurements).result()
            counts = result.get_counts()
            #print(counts)
            #counts the results for each qubit
            nb0s = 0
            for elem in counts:
                #Bit oredering is in the reverse order for get_count
                #(if we measure the last bit, it will get its value in index 0 of the string for some reason)
                if elem[::-1][measuredBit] == '0': nb0s += counts[elem]


            trialProba = nb0s / nbMeasurements

            trialProbas[trialIndex] = trialProba
        #print(trialProbas)
        return trialProbas


    #Returns a tuple of tuple of bool
    #Data to collect is a tuple (one for each trial) of tuples (one for each trial) of bools (one for each measruement)
    def runTestsAssertProbability(self,
                                  initialisedTests,
                                  nbTrials: int,
                                  nbMeasurements: int,
                                  qu0,
                                  measuredBit):
        retList = []
        for qc in initialisedTests:
           retList.append(self.runTestAssertProbability(qc, nbTrials, nbMeasurements, qu0, measuredBit))
        return retList


    def runTestAssertTransformed(self,
                                 qc,
                                 nbTrials,
                                 nbMeasurements,
                                 qu0):
        sim = Aer.get_backend('statevector_simulator')

        qc = self.applyQuantumFunction(qc, inputProg, filename)

        #qc.draw(output="mpl")
        #plt.show()

        result = sim.run(qc, shots = nbMeasurements).result()
        #print('Statevecotor: ', result.get_statevector())
        return result.get_statevector()

    def runTestsAssertTransformed(self,
                                  tests,
                                  nbTrials,
                                  nbMeasurements,
                                  qu0):
        retList = []
        for qc in tests:
            retList.append(runTestAssertTransformed(qc, nbTrials, nbMeasurements, qu0))
        return retList
