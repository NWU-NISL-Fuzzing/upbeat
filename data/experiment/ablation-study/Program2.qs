// can be detected by upbeat-a&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Chemistry.JordanWigner;

    @EntryPoint()
    operation main() : Unit {
        //correct
        mutable nFermions = [1,2,3,4];
        mutable idxFermions = 2^63-1;
        let bitString4159 = _ComputeJordanWignerBitString(nFermions, idxFermions);
    }
}