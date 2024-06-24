namespace NISLNameSpace {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.ErrorCorrection;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        use aux1051 = Qubit[2];
        Ry(PI() / 4.0, aux1051[1]);
        let expected1051 = ApplyToEachA(Ry(-PI() / 4.0, _), _);
        let actual1051 = ApplyToEach(Adjoint InjectPi4YRotation(_, aux1051[1]), _);
        Reset(aux1051[0]);
        
        let tempQubits1346 = aux1051;
        use a11346 = Qubit();
        // Modify initial state(s) of qubit(s). 
        T(a11346);
        // Modify end. 
        use b11346 = Qubit();
        // Modify initial state(s) of qubit(s). 
        Z(b11346);
        // Modify end. 
        Sum(tempQubits1346[0],a11346,b11346);
        
        DumpMachine();
        ResetAll(tempQubits1346);
        Reset(a11346);
        Reset(b11346);
        ResetAll(aux1051);
        
    }
}