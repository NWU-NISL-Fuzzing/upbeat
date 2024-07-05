namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;


    
    @EntryPoint()
    operation main() : Unit {
        // Delete Gate
        //no cons
        use target759QubitArray = Qubit[2];
        // Modify initial state(s) of qubit(s). 
        // Modify end. 
        mutable target759 = BigEndian(target759QubitArray);
        let (q1759, q2759, q3759) = ((target759!)[0], (target759!)[1], (target759!)[2]);

        let qubit10 = q1759;
        H(qubit10);
        DumpMachine();
        Reset(qubit10);
        Reset(qubit10);
        Reset(q1759);
        Reset(q2759);
        Reset(q3759);
        
    }
}