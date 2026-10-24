# Engineering model and units

Inverter |Q|≤sqrt(S²−P²), further restricted by q_limit. Tap ratio a=1+nΔa acts on the branch from side. Capacitor Q=n Qstep |V|². Displacement PF=|P|/sqrt(P²+Q²). Objective = wloss Ploss + wvoltage Σ(|V|−1)² + wswitch Σ|u−uprevious|. Feasibility is separate from the objective; voltage, loading, PF and convergence must all pass. Q commands are interpolated along an ordered curve and damped during local iteration.

Network powers use MW/MVAr, branch impedances and taps use the stated system per-unit base, bus voltage is per unit, angles are degrees at interchange and radians inside equations. Loads draw positive P/Q; inverter and generator positive Q means injection. Transformer branch direction matters. Equipment source ratings must be verified for the project.

Balanced positive-sequence steady state. GridFlow core is pinned and vendored under MIT. The coordinated optimizer is globally optimal only on its stated finite tap/capacitor/Q grid, with a candidate-count limit. It is not continuous AC OPF. Local controls are simultaneous bounded heuristics and can cycle; cycles and iteration limits are explicitly marked unsuccessful. Chronological optimization is myopic, with switching penalties against the previous accepted state. Inverter devices attach to PQ buses only. Capacitors are physical shunts whose MVAr varies with V². Fixed-command solar stress tests are not robust optimization. Source/slack Q limits, installation approval and switching transients require separate study.

Primary references, consulted 2026-10-24: [EPRI reactive-control conventions](https://opendss.epri.com/PropertiesoffunctionsthatCONTROL.html). Capability and control conventions are explicit; no IEEE/IEC conformance assertion is made.
