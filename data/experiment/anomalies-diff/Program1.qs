// Bug Description:
// Can be detected by qdiff&morphq&upbeat-r&upbeat.
// The measured qubits are larger than declared when running on SparseSimulator. 

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Convert;

    @EntryPoint()
    operation main() : Unit {
        use xs2052QubitArray = Qubit[3];
        mutable xs2052 = SignedLittleEndian(LittleEndian(xs2052QubitArray));
        use aux = Qubit[Length(xs2052!!)]{}
        use target5292 = Qubit();
        let angle = -PI() / 2.0;
        Message($"{angle}");
        R(PauliX, angle, target5292);
        DumpMachine();
        Reset(target5292);
        ResetAll(xs2052QubitArray);
    }
}