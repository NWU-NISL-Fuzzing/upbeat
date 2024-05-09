## Bug List(API Implementation)

| No.  |     API     |     Version      |                             Link                             | Status                         | Contributor                              | Description   |
| :--: | :--------------: | :----------------------------------------------------------: | ------------------------------ | ---------------------------------------- | ------------------------------------------------ | ---- |
|  1   | Binom | V0.21.2111177148 | [Bug Report1](https://github.com/microsoft/QuantumLibraries/issues/498) | First Found & Verified & Fixed | [Xing Qu](https://github.com/QuXing9)    | k=0 or n=k will cause an overflow |
| 2 | HalfIntegerBinom | v0.21.2111177148 | [Bug-Report2](/docs/bug/bug-14.png) | Verified & Fixed | [Xing Qu](https://github.com/QuXing9) | k=0 will cause overflow |
| 3 | Sin | v0.25.228311 | [Bug-Report3](https://github.com/microsoft/QuantumLibraries/issues/624) | First Found & Verified | [Tianmin Hu](https://github.com/weucode) | different os has different outputs for theta=PI()/4 |
| 4 | Ceiling | v0.25.228311 | [Bug-Report4](https://github.com/microsoft/qsharp-runtime/issues/1107) | First Found & Verified | [Tianmin Hu](https://github.com/weucode) | NaN() cause an overflow |
| 5 | Truncate | v0.27.258160 | [Bug-Report5](https://github.com/microsoft/qsharp-runtime/issues/1139) | Submit | [Tianmin Hu](https://github.com/weucode) | send a large number to the argument will cause an overflow |
| 6 | IncrementPhaseByModularInteger | v0.25.228311 | [Bug-Report6](https://github.com/microsoft/QuantumLibraries/issues/639) | Submit | [Qianbao He](https://github.com/hofirstb19) | has unknown qubits are unreleased |
| 7 | IdenticalPointPosFactFxP | v0.27.238334 | [Bug-Report7](https://github.com/microsoft/QuantumLibraries/issues/645) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | check is out of work when Length(fixedPoint)=2 |
|  8   |   Chunks   |   v0.23.195983   | [Bug Report8](https://github.com/microsoft/QuantumLibraries/issues/538) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | nElements=0 cause a timeout |
| 9 | SequenceL | v0.27.258160 | [Bug-Report9](https://github.com/microsoft/QuantumLibraries/issues/662) | Submit | [Tianmin Hu](https://github.com/weucode) | error check for to-from |
|  10  | IntAsBoolArray | V0.21.2111177148 | [Bug Report10](https://github.com/microsoft/QuantumLibraries/issues/503) | First Found & Verified & Fixed | [Xing Qu](https://github.com/QuXing9)    | bits = 63 will fail to convert |
| 11 | Parity | v0.24.201332 | [Bug-Report11](https://github.com/microsoft/qsharp-runtime/issues/993) | First Found & Verified | [Xing Qu](https://github.com/QuXing9) | failed when a is negetive |
| 12 | PurifiedMixedStateRequirements | v0.24.201332 | [Bug-Report12](https://github.com/microsoft/QuantumLibraries/issues/570) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | a non-positive argument will cause overflow |
| 13 | AssertQubitWithinTolerance | 0.24.201332 | [Bug-Report13](https://github.com/microsoft/qsharp-runtime/issues/990) | Submit | [Xing Qu](https://github.com/QuXing9) | always raises unexception with a wrong judge when tolerance is negative |
| 14 | DumpMachine | v0.24.201332 | [Bug-Report14](https://github.com/microsoft/qsharp-runtime/issues/1081#issuecomment-1518472023) | Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | the qubit states is encoded in big-endian instead of little-endian |
| 15 | DumpRegister | v0.28.263081 | [Bug-Report15](https://github.com/microsoft/QuantumLibraries/issues/671) | Submit | [Zhenye Fan](https://github.com/AidPaike) | failed to report the given qubits are entangled with some other qubits |
| 16 | Adjoint ApplyAnd | v0.28.277227 | [Bug-Report16](https://github.com/microsoft/QuantumLibraries/issues/677) | Submit | [Tianmin Hu](https://github.com/weucode) | ToffoliSimulator outputs different result compared to other simulators |



## Bug List(API Document)

| No.  | API                           | Version      | Link                                                         | Status                         | Contributor                              | Description                                                  |
| ---- | ----------------------------- | ------------ | ------------------------------------------------------------ | ------------------------------ | ---------------------------------------- | ------------------------------------------------------------ |
| 1    | Padded                        | v0.24.201332 | [Bug-Report1](https://github.com/microsoft/QuantumLibraries/issues/554) | First Found & Verified & Fixed | [Xing Qu](https://github.com/QuXing9)    | wrong argument order                                         |
| 2    | Last                          | v0.24.201332 | [Bug-Report2](https://github.com/microsoft/QuantumLibraries/issues/563) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | the example contains APIs that have been deprecated in the latest SDK version |
| 3    | ApproximateFactorial          | v0.24.201332 | [Bug-Report3](https://github.com/microsoft/QuantumLibraries/issues/571) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | the boundary description is wrong                            |
| 4    | _ComputeJordanWignerBitString | v0.25.228311 | [Bug-Report4](https://github.com/microsoft/QuantumLibraries/issues/646) | First Found & Verified & Fixed | [Tianmin Hu](https://github.com/weucode) | the value of the first argument is wrong                     |

