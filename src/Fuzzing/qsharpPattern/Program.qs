namespace NISLNameSpace {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Arithmetic;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        using (qs = Qubit[2]) {
            SWAP(qs[0], qs[1]);
            DumpRegister((), qs);
            ResetAll(qs);
            DumpMachine();
            ResetAll(qs);
        }
        
    }
}