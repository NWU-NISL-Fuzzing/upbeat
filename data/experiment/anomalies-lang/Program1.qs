// can be detected by qdiff&morphq&upbeat-r&upbeat

namespace NameSpace {
	open Microsoft.Quantum.Intrinsic;
	open Microsoft.Quantum.Math;


	@EntryPoint()
	operation main() : Unit {
        let nIdxRegQubits = Ceiling(NaN());
		Message($"{nIdxRegQubits}");
	}
}