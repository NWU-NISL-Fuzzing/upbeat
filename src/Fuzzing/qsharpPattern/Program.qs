namespace NISLNameSpace {
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.MachineLearning;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        let left275 = [1, 2, 101];
        let right275 = [PauliY, PauliI];
        let zipped275 = Zipped(left275, right275);
        
        let localPL1129 = left275;
        mutable labels1129 = [1,-1,-2];
        let nMisclassifications1129 = NMisclassifications(localPL1129, labels1129);
        let returnVar1129 = ValidationResults(nMisclassifications1129,Length(localPL1129));
        
        Message($"{nMisclassifications1129}");
        Message($"{returnVar1129}");
        
    }
}