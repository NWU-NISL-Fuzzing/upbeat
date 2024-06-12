// can be detected by upbeat-b&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    @EntryPoint()
    operation main() : Unit {
        let a = 2^63;
        let _ = BitSizeI(a);
    }
}