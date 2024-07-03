// Bug Description:
// Can be detected by upbeat-a&upbeat.
// Time out occurs when running on QuantumSimulator. 

namespace NISLNameSpace {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;


    @EntryPoint()
    operation main() : Unit {
        mutable n = 5;
        use aqs = Qubit[n];
        use cqs = Qubit[2 * n];
        ComputeReciprocalI(LittleEndian(aqs), LittleEndian(cqs));
        ResetAll(aqs);
        ResetAll(cqs);
    }
}