// can be detected by qsharpfuzz

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
        let q = BadAlloc(); 
        H(q); 
        Reset(q); 
    } 
}