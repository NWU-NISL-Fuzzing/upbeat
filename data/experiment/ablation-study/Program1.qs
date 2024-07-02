// Bug Description:
// Can be detected by upbeat-a&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    @EntryPoint()
    operation main() : Unit {
        let k = 34;
        let _ = Binom(k*2, k);
    }
}