// Bug Description:
// Can be detected by upbeat.
// QuantumSimulator run successfully.

namespace NameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Arithmetic;

	@EntryPoint()
	operation main() : Unit {
        use q1 = Qubit[3];
		mutable a = FixedPoint(2, q1);
		use q2 = Qubit[3];
		mutable b = FixedPoint(4, q2);
        let fixedPoints = [a, b];
		IdenticalPointPosFactFxP(fixedPoints);
	}
}