// Bug Description:
// Can be detected by qsharpfuzz&upbeat.
// ToffoliSimulator throws a ReleasedQubitsAreNotInZeroState exception, while other two simulators run successfully.

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    
    @EntryPoint() operation main() : Unit {
        use q2 = Qubit();
        X(q2);
        let b2 = M(q2);
    }
}