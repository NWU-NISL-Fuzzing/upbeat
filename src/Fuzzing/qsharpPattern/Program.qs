namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Math;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        mutable nVertices1491 = 1;
        let edges1491 = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3), (3,4)];
        let coloring1491 = [false, false, true, false, false, true, true, true, true, false];
        let colors1491 = ["red", "green", "blue", "yellow"];
        let colorBits1491 = Chunks(2, coloring1491);
        for (i in 0..nVertices1491-1) {
            let colorIndex = BoolArrayAsInt(colorBits1491[i]);
            Message ($"Vertex {i} - color #{colorIndex} ({colors1491[colorIndex]})");
        }
        let example306 = edges1491;
        let actual306 = Mapped(SequenceI, example306);
        Message($"{actual306}");
        
    }
}