namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.ErrorCorrection;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Math;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        use logicalRegisterQubitArray = Qubit[4];
        // Modify initial state(s) of qubit(s).
        // Modify end.
        mutable logicalRegister = LogicalRegister(logicalRegisterQubitArray);
        mutable APIResult = DecodeFromSteaneCode(logicalRegister);
        Message($"{APIResult}");
        
        DumpMachine();
        
    }
}