// can be detected by upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    @EntryPoint()
    operation main() : Unit {
        let _ = BitSizeI(2^63);
    }
}
