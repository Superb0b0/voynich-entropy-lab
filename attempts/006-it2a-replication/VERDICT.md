# Attempt 006 - replica dello stesso test sulla trascrizione IT2a (Takahashi) - verdetto

Verdetto da results.json: **NOT SUPPORTED** (criterio di PROTOCOL.md). ESPLORATIVO, non qualificante; CI GitHub non ancora verde -> NON VERIFICATO fino al job verde.

Gruppi e coppie valide per split: {"0": {"n_groups": 124, "valid_pairs": 1871}, "1": {"n_groups": 82, "valid_pairs": 1224}}

## fit0_pred1
theta_nonqo=0.868927, phi=0.981579, theta_all=0.959568

| metrica | osservato | M2 media [2,5%;97,5%] | dentro M2 | M1 media [2,5%;97,5%] | dentro M1 |
|---|---|---|---|---|---|
| same_nonqo | 128 | 111.115 [93;127] | False | 104.9 [89;123] | False |
| qoqo | 2 | 3.01 [0;6] | True | 6.86 [3;11] | False |
| repeat | 5 | 4.465 [1;8] | True | 4.55 [1;9] | True |

## fit1_pred0
theta_nonqo=0.691337, phi=1.677419, theta_all=0.766193

| metrica | osservato | M2 media [2,5%;97,5%] | dentro M2 | M1 media [2,5%;97,5%] | dentro M1 |
|---|---|---|---|---|---|
| same_nonqo | 161 | 176.965 [153;199] | True | 168.355 [148;194] | True |
| qoqo | 12 | 8.11 [4;14] | True | 28.155 [19;38] | False |
| repeat | 7 | 6.22 [2;11] | True | 7.24 [3;13] | True |

Criteri: {"M1_qoqo_excluded_both_directions": true, "M2_all_inside_both_directions": false, "verdict": "NOT SUPPORTED"}
