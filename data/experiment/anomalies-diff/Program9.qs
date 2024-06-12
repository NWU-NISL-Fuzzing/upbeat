// can be detected by upbeat

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