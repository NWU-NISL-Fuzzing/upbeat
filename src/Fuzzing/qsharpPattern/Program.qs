namespace NISLNameSpace {
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.AmplitudeAmplification;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Diagnostics;


    @EntryPoint()
    operation main() : Unit {
        //no cons
        mutable phases = ReflectionPhases([0.8640128849202899,1.014362621348742222,2.040425272633736076,49.2444619203454269,0.2683836106674311], [-9.867988917592552,-706.25041550185836126,3.024875474608757386,-97.38208898898285604,0.9643928683444909]);
        mutable startStateReflection = ReflectionOracle(RAll0);
        mutable targetStateReflection = ReflectionOracle(RAll0);
        mutable APIResult = AmplitudeAmplificationFromPartialReflections(phases, startStateReflection, targetStateReflection);
        DumpMachine();
        Message($"{phases}");
        Message($"{startStateReflection}");
        Message($"{targetStateReflection}");
        
    }
}