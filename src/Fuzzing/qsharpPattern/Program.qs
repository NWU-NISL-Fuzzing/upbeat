namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Canon;


    
    @EntryPoint()
    operation main() : Unit {
        //valid
        mutable coefficients983 = EmptyArray<Double>();
        let oneNorm983 = PNorm(1.0, coefficients983);
        Message($"{oneNorm983}");
        
    }
}