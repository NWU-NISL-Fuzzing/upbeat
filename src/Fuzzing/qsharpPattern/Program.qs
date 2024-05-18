namespace NISLNameSpace {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Oracles;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.MachineLearning;
    open Microsoft.Quantum.Logical;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;


    
    @EntryPoint()
    operation main() : Unit {
        //no cons
        //no cons
        mutable samples2968 = [LabeledSample(([0.510784, 0.475476, 0.453884, 0.554087], 0)),LabeledSample(([0.581557, 0.562824, 0.447721, 0.380219], 1))];
        mutable options2968 = TrainingOptions(0.1, 0.005, 15, 10000, 16, 8, 0.01, 1,Ignore<String>);
        mutable optimizedModel2968 = SequentialModel([ControlledRotation((2, [0]), PauliX, 0),ControlledRotation((0, [1, 2]), PauliZ, 1)],[1.234, 2.345],0.0);
        mutable validationSchedule2968 = SamplingSchedule([4..-10..5,-4..-5..7,-5..4..-8,-1..-2..-3]);
                let features2968 = Mapped(_Features, samples2968);
        let probabilities2968 = EstimateClassificationProbabilities(options2968::Tolerance,optimizedModel2968,Sampled(validationSchedule2968, features2968),options2968::NMeasurements);
        let count4069 = probabilities2968;
        mutable Nruns4069 = -2^63;
        mutable sin_2piPhi4069 = 1.2620648877763516;
                let p0_cos4069 = count4069[1]/IntAsDouble(Nruns4069);
                let cos_2piPhi4069 = 2.0*p0_cos4069-1.0;
                if (cos_2piPhi4069 > 0.0) {if (sin_2piPhi4069 >0.0) {let phi = ArcTan(sin_2piPhi4069/cos_2piPhi4069)/(2.0*PI());                let returnVar = phi;}else {let phi = ArcTan(sin_2piPhi4069/cos_2piPhi4069)/(2.0*PI());
                        let returnVar = 1.0+phi; }}else {if (sin_2piPhi4069 > 0.0) {let phi = ArcTan(sin_2piPhi4069/cos_2piPhi4069)/(2.0*PI());
                        let returnVar = 0.5+phi; }else {let phi = ArcTan(sin_2piPhi4069/cos_2piPhi4069)/(2.0*PI());
                        let returnVar = 0.5+phi; }}Message($"{p0_cos4069}");
        Message($"{cos_2piPhi4069}");
        
    }
}