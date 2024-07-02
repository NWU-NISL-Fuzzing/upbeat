// Bug Description:
// Can be detected by upbeat-a&upbeat.
// Time out occurs when running on QuantumSimulator. 

namespace NISLNameSpace {
    open Microsoft.Quantum.Arrays;

    @EntryPoint()
    operation main() : Unit {
        mutable chunkSize = 0;
		mutable array = [1,2,3];
		mutable result = Chunks(chunkSize, array);
    }
}