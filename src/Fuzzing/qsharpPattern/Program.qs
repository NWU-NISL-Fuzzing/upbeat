namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;


    
    @EntryPoint()
    operation main() : Unit {
        // Delete Statement
        using (qs = Qubit[2]) {
            SWAP(qs[0], qs[1]);
            DumpRegister((), qs);
            DumpMachine();
            ResetAll(qs);
        }    }
}