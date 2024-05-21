namespace NISLNameSpace {
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Oracles;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        mutable time4915 = 1.0;
        mutable prob4915 = Sin(time4915) * Sin(time4915);
        use qubits4915 = Qubit[4];
        X(qubits4915[0]);
        X(qubits4915[1]);
        DumpMachine();
        Message($"{time4915}");
        Message($"{prob4915}");
        ResetAll(qubits4915);
        
    }
}