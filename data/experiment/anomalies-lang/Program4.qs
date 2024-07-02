// Bug Description:
// Can be detected by upbeat-m&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NISLNameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Bitwise;

	@EntryPoint()
	operation main() : Unit {
		mutable a = -1;
		let b = Parity(-1);
	}
}