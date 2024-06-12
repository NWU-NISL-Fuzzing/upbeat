// can be detected by qsharpfuzz&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    
    @EntryPoint() 
    operation main() : Unit {
        use qs = Qubit[2] {
            X(qs[1]);
        }
    }
}