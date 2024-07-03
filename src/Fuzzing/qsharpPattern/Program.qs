namespace NISLNameSpace {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Math;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        use register2039QubitArray = Qubit[6];
        // Modify initial state(s) of qubit(s). 
        // Modify end. 
        mutable register2039 = BigEndian(register2039QubitArray);
        QFT(register2039);
        mutable bitwidth2 = 20;
        //no cons
        use factor12 = Qubit[bitwidth2];
        use factor22 = Qubit[bitwidth2];
        use product2 = Qubit[2 * bitwidth2];
        MultiplyI(LittleEndian(factor12), LittleEndian(factor22), LittleEndian(product2));
        DumpMachine();
        ResetAll(product2);
        ResetAll(factor22);
        ResetAll(factor12);
        
    }
}