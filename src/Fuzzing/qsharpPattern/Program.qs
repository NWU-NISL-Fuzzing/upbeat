namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Math;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        mutable time6203 = -1.8018458518464863;
        mutable dt6203 = -1.40339372615444147;
        let nSteps6203 = Floor(time6203 / dt6203);
        
        let targetRegisterSize4419 = nSteps6203;
        let indexRegisterSize4419 = Ceiling(Lg(IntAsDouble(targetRegisterSize4419)));
        use targetRegister4419 = Qubit[targetRegisterSize4419];
        
        DumpMachine();
        Message($"{indexRegisterSize4419}");
        ResetAll(targetRegister4419);
        
    }
}