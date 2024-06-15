namespace NISLNameSpace {
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        mutable A3727 = ConstantArray(11, 1);
        Message($"{A3727}");
        
    }
}