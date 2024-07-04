// Bug Description:
// Can be detected by upbeat.
// QuantumSimulator and SparseSimulator throw the ArgumentNullException exception, while ToffoliSimulator run successfully.

namespace NISLNameSpace {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;


    @EntryPoint()
    operation main() : Unit {
        use qs = Qubit[0];
        DumpRegister((), qs);
        ResetAll(qs);
    }
}