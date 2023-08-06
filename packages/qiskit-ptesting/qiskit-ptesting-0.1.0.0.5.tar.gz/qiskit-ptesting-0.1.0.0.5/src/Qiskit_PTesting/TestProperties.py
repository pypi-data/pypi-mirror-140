class Qarg:
    def __init__(self,
                 minTheta,
                 maxTheta,
                 minPhi,
                 maxPhi):

        #Error handling on Qarg values
        if minTheta < 0 or minTheta > 360:
            raise Exception(f"Invalid minTheta supplied, it has to be between 0 and 360 inclusive: {minTheta}")
        if maxTheta < 0 or maxTheta > 360:
            raise Exception(f"Invalid maxTheta supplied, it has to be between 0 and 360 inclusive: {maxTheta}")
        if minPhi < 0 or minPhi > 360:
            raise Exception(f"Invalid minPhi supplied, it has to be between 0 and 360 inclusive: {minPhi}")
        if maxPhi < 0 or maxPhi > 360:
            raise Exception(f"Invalid maxPhi supplied, it has to be between 0 and 360 inclusive: {maxPhi}")

        self.minTheta = minTheta
        self.maxTheta = maxTheta
        self.minPhi = minPhi
        self.maxPhi = maxPhi


class TestProperty:
    def __init__(self,
                p_value,
                nbTests,
                nbTrials,
                nbMeasurements,
                nbQubits,
                nbClassicalBits,
                preconditions_q):

        #Error handling on all values for the test property
        if p_value < 0 and p_value > 1:
            raise Exception(f"Invalid p_value supplied: {p_value}")
        elif nbTests < 1:
            raise Exception(f"Invalid amount of tests supplied: {nbTests}")
        elif nbTrials < 1:
            raise Exception(f"Invalid number of trials supplied: {nbTrials}")
        elif nbMeasurements < 1:
            raise Exception(f"Invalid number of measurements supplied: {nbMeasurements}")
        elif nbQubits < 1:
            raise Exception(f"Invalid number of qubits supplied: {nbQubits}")
        elif nbClassicalBits < 0:
            raise Exception(f"Invalid number of classical bits supplied: {nbClassicalBits}")

        for key, value in preconditions_q.items():
            if key < 0 or key >= nbQubits:
                raise Exception(f"Invalid qubit index in the dictionary supplied: {(key, value)}")

        self.p_value = p_value
        self.nbTests = nbTests
        self.nbTrials = nbTrials
        self.nbMeasurements = nbMeasurements
        self.nbQubits = nbQubits
        self.nbClassicalBits = nbClassicalBits
        self.preconditions_q = preconditions_q
