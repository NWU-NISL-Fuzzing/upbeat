// Bug Description:
// Can be detected by qdiff&morphq&upbeat-r&upbeat.
// QuantumSimulator throws an OverflowException exception.

namespace NameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Math;


	@EntryPoint()
	operation main() : Unit {
        let nIdxRegQubits = Ceiling(NaN());
		Message($"{nIdxRegQubits}");
	}
}