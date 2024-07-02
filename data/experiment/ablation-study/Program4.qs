// Bug Description:
// Can be detected by upbeat-a&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NISLNameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Bitwise;

	@EntryPoint()
	operation main() : Unit {
        let a = 2^63;
		let _ = Parity(a);
	}
}