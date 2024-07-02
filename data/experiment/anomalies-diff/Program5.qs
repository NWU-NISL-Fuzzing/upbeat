// Bug Description:
// Can be detected by upbeat-m.
// QuantumSimulator throws a InvalidOperationException exception, while other simulators throws a OutOfMemoryException exception.

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Characterization;

    
    @EntryPoint()
    operation main() : Unit {
        mutable inputStateUnitary = AssertAllZero;
        mutable op = [PauliY,PauliY,PauliI,PauliY,PauliY];
        mutable nQubits = 2147483647;
        mutable nSamples = 2147483647;
        let termExpectation = EstimateFrequencyA(inputStateUnitary, Measure(op, _), nQubits, nSamples);        
    }
}