// Bug Description:
// Can be detected by upbeat-a&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NISLNameSpace {
	open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Convert;

	@EntryPoint()
	operation main(): Unit {
		let var = 0;
        let _ = Ceiling(Lg(IntAsDouble(var)));
	}
}