// can be detected by upbeat-a&upbeat

namespace NISLNameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Bitwise;

	@EntryPoint()
	operation main() : Unit {
        let a = 2^63-1;
		let _ = Parity(a);
	}
}