// can be detected by qsharpfuzz

namespace NISLNameSpace {
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;

    operation func1(target: Qubit) : Unit is Adj + Ctl {
        X(target);
    }
    
    @EntryPoint() 
    operation main() : Unit {
        use coloringRegister = Qubit();
        func1(coloringRegister);
        DumpMachine();
    }
}