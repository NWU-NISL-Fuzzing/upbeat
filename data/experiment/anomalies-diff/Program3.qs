// can be detected by qsharpfuzz&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    
    @EntryPoint() operation main() : Unit {
        use q2 = Qubit();
        X(q2);
        let b2 = M(q2);
    }
}