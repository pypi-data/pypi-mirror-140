## Topsis-Manish-101903228

# TOPSIS

Submitted By: **Manish Sharma - 101903228**.

Type: **Package**.

Title: **TOPSIS method for multiple-criteria decision making (MCDM)**.

Version: **0.0.2**.

Date: **26-Feb-2022**.

Author: **Manish Sharma**.

Contact: **<manish1206s@gmail.com>**.

Submitted To :**Dr. Prashant Singh Rana**

Description: **Evaluation of alternatives based on multiple criteria using TOPSIS method.**.

---

## What is TOPSIS?

**T**echnique for **O**rder **P**reference by **S**imilarity to **I**deal **S**olution
(TOPSIS) originated in the 1980s as a multi-criteria decision making method.
TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution,
and greatest distance from the negative-ideal solution.

<br>

## How to install this package:

```
>> pip install Topsis-Manish-101903228
```

### In Command Prompt Run with the following parameters

```
>> topsis input_data_file.csv "1,1,1,1,1" "+,-,+,-,+" result.csv
```

## Input file (input_data_file.csv)

The decision matrix should be constructed with each row representing a Model alternative, and each column representing a criterion.

| Model | p1          | p2            | p3   |p4        |
| ----- | ----------- | ------------- | ---- | -------- |
| M1    | 0.11        | 0.2           | 1.85 | 70.89    |
| M2    | 0.68        | 0.454         | 2.89 | 73.07    |
| M3    | 0.56        | 0.31          | 1.57 | 2.87     |



Weights (`weights`) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in `impacts`.

<br>

## Output file (result.csv)


| Model | p1          | p2            | p3   |p4        | Topsis_score | Rank |
| ----- | ----------- | ------------- | ---- | -------- | ------------ | ---- |
| M1    | 0.11        | 0.2           | 1.85 | 70.89    | 0.5722       | 3    |
| M2    | 0.68        | 0.454         | 2.89 | 73.07    | 0.7722       | 2    |
| M3    | 0.56        | 0.31          | 1.57 | 2.87     | 0.7872       | 1    |

<br>
The output file contains columns of input file along with two additional columns having (Topsis score) and (Rank)