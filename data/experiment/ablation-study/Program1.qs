// can be detected by upbeat-a&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    @EntryPoint()
    operation main() : Unit {
        let k = 34;
        let _ = Binom(k*2, k);
    }
}