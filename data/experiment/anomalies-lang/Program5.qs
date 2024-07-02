// Bug Description:
// Can be detected by qsharpfuzz.
// QuantumSimulator throws a ReleasedQubitsAreNotInZeroState exception.

namespace NISLNameSpace { 
    open Microsoft.Quantum.Intrinsic; 
    
    operation func1(): Qubit { 
        use q = Qubit() { 
            X(q); 
            return q; 
        } 
    } 
    
    @EntryPoint() 
    operation main(): Unit { 
        let q = func1(); 
        H(q); 
        Reset(q); 
    } 
}