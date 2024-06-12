// can be detected by upbeat-r

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Characterization;
    open Microsoft.Quantum.Diagnostics;


    operation NoOp55 (arg : Qubit[]) : Unit is Adj {}

    operation NoOp82 (arg : Qubit[]) : Unit is Adj {}

    @EntryPoint()
    operation main() : Unit {
        mutable NISLParameter0 = 21474836470;
        mutable NISLParameter3 = 0;
        mutable NISLVariable0 = EstimateOverlapBetweenStates(NoOp55,NoOp82,NISLParameter0,NISLParameter3);
        Message($"{NISLVariable0}");
    }
}