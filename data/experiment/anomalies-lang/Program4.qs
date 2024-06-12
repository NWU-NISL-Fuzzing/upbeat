// can be detected by upbeat-m&upbeat

namespace NISLNameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Bitwise;

	@EntryPoint()
	operation main() : Unit {
		Message($"{Parity(-1)}");
	}
}