# Attempt 005 - modello refrattario di classe con parametro specifico per qo (ZL3b) - verdetto

Verdetto da results.json: **SUPPORTED** (criterio di PROTOCOL.md). ESPLORATIVO, non qualificante; CI GitHub non ancora verde -> NON VERIFICATO fino al job verde.

Gruppi e coppie valide per split: {"0": {"n_groups": 124, "valid_pairs": 1871}, "1": {"n_groups": 82, "valid_pairs": 1226}}

## fit0_pred1
theta_nonqo=0.815843, phi=1.091503, theta_all=0.914629

| metrica | osservato | M2 media [2,5%;97,5%] | dentro M2 | M1 media [2,5%;97,5%] | dentro M1 |
|---|---|---|---|---|---|
| same_nonqo | 126 | 113.355 [95;133] | True | 106.75 [91;124] | False |
| qoqo | 2 | 3.075 [1;7] | True | 7.025 [3;12] | False |
| repeat | 7 | 4.93 [2;9] | True | 5.175 [1;9] | True |

## fit1_pred0
theta_nonqo=0.694776, phi=1.675, theta_all=0.766643

| metrica | osservato | M2 media [2,5%;97,5%] | dentro M2 | M1 media [2,5%;97,5%] | dentro M1 |
|---|---|---|---|---|---|
| same_nonqo | 163 | 175.49 [151;200] | True | 170.0 [150;193] | True |
| qoqo | 12 | 7.545 [3;13] | True | 28.165 [21;36] | False |
| repeat | 6 | 6.38 [2;11] | True | 7.425 [3;12] | True |

Criteri: {"M1_qoqo_excluded_both_directions": true, "M2_all_inside_both_directions": true, "verdict": "SUPPORTED"}
