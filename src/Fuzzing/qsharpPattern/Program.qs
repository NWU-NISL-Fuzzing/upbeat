namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Core;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        mutable nDatabaseQubits6373 = 1;
                let databaseSize6373 = 2 ^ nDatabaseQubits6373;
                let markedElements6373 = [0, 39, 101, 234];
                let nMarkedElements6373 = Length(markedElements6373);
                let nIterations6373 = 3;
                let queries6373 = nIterations6373 * 2 + 1;
                let classicalSuccessProbability6373 = IntAsDouble(nMarkedElements6373) / IntAsDouble(databaseSize6373);
                let quantumSuccessProbability6373 = Sin((2.0 * IntAsDouble(nIterations6373) + 1.0) * ArcSin(Sqrt(IntAsDouble(nMarkedElements6373)) / Sqrt(IntAsDouble(databaseSize6373)))) ^ 2.0;
        let nItems5106 = databaseSize6373;
                let angle5106 = ArcSin(1. / Sqrt(IntAsDouble(nItems5106)));
        Message($"{angle5106}");
        
    }
}