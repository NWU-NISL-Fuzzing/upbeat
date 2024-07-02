// Bug Description:
// Can be detected by upbeat.
// ToffoliSimulator outputs |111>, while other two simulators output |110>.

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Math;

    @EntryPoint()
    operation main() : Unit {
        use t1 = Qubit();
        X(t1);
        use t2 = Qubit();
        X(t2);
        use qs = Qubit();
        Adjoint ApplyAnd(t1, t2, qs);
        DumpMachine();
        ResetAll([t1,t2,qs]);
    }
}