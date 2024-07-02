// Bug Description:
// Can be detected by qsharpfuzz.
// ToffoliSimulator throws a ReleasedQubitsAreNotInZeroState exception, while other two simulators run successfully.

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