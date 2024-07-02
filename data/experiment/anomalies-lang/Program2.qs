// Bug Description:
// Can be detected by upbeat-r&upbeat.
// QuantumSimulator throws a ReleasedQubitsAreNotInZeroState exception.

namespace NISLNameSpace {
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;


    @EntryPoint()
    operation main() : Unit {
        mutable increment = 1;
        let targetQubitArrayLen = 3;
        let modulus = 4;
        use targetQubitArray = Qubit[3];
        let target = PhaseLittleEndian(targetQubitArray);
        mutable APIResult = IncrementPhaseByModularInteger(increment, modulus, target);
        DumpMachine();
        ResetAll(targetQubitArray);
    }
}