// Bug Description:
// Can be detected by qsharpfuzz&upbeat.
// ToffoliSimulator throws a ReleasedQubitsAreNotInZeroState exception, while other two simulators run successfully.

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    
    @EntryPoint() 
    operation main() : Unit {
        use qs = Qubit[2] {
            X(qs[1]);
        }
    }
}