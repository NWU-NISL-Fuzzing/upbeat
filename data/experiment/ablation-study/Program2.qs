// Bug Description:
// Can be detected by upbeat-a&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NISLNameSpace {
    open Microsoft.Quantum.Chemistry.JordanWigner;

    @EntryPoint()
    operation main() : Unit {
        mutable nFermions = [1,2,3,4];
        mutable idxFermions = 2^63-1;
        let bitString4159 = _ComputeJordanWignerBitString(idxFermions, nFermions);
    }
}