namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Arithmetic;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        use register6059 = Qubit[1];
        // Modify initial state(s) of qubit(s). 
        ApplyToEach(T, register6059);
        // Modify end. 
        let ket0 = (Complex(1.0, 0.0), Complex(0.0, 0.0));
        let angle6059 = (PI() * 5.0) / 7.0;
        H(register6059[0]);
        Exp([PauliZ, PauliZ], angle6059, register6059);
        H(register6059[0]);
        Exp([PauliX, PauliI], -angle6059, register6059);
        DumpMachine();
        Message($"{angle6059}");
        ResetAll(register6059);
        
    }
}