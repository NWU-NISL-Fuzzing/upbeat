namespace NISLNameSpace {
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Arrays;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
                let realUnit8337 = Complex(1.0, 0.0);
        let res7824 = realUnit8337;
        mutable phase7824 = Complex(0.18296663298216342, 0.39981329119622466);
        let (reRes7824, imRes7824) = (TimesC(res7824, phase7824))!;
        let returnVar7824 = reRes7824;
        Message($"{reRes7824}");
        Message($"{imRes7824}");
        Message($"{returnVar7824}");
        
    }
}