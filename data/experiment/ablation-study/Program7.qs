// can be detected by upbeat-b&upbeat

namespace NISLNameSpace {
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Intrinsic;
    
    @EntryPoint()
    operation main() : Unit {
        //correct
        use xsQubitArray = Qubit[0];
        mutable xs = LittleEndian(xsQubitArray);
        use ysQubitArray = Qubit[0];
        mutable ys = LittleEndian(ysQubitArray);
        use result = Qubit();
        mutable APIResult = GreaterThan(xs, ys, result);
        ResetAll(xsQubitArray);
        ResetAll(ysQubitArray);
        Reset(result);
    }
}