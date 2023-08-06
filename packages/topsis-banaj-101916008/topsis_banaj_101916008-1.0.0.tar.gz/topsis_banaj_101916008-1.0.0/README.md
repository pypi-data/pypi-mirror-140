# TOPSIS

Submitted By: **Banaj Bedi**.

Type: **Package**.

Title: **TOPSIS method for multiple-criteria decision making (MCDM)**.

Version: **1.0.0**.
<br>
Date: **2022-02-26**.
<br>
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
>> pip install topsis_banaj_101916008
```

### In Command Prompt

```
>> topsis data.csv "1,1,2,1,2" "+,+,-,-,+" result.csv
```

## Input file (data.csv)

The decision matrix should be constructed with each row representing a Model alternative, and each column representing a criterion like Accuracy, R<sup>2</sup>, Root Mean Squared Error, Correlation, and many more.

![image](https://user-images.githubusercontent.com/83486603/155836677-32ab8148-315c-42ff-b949-795dc881c059.png)



Weights (`weights`) is not already normalised will be normalised later in the code.

Information of benefit positive(+) or negative(-) impact criteria should be provided in `impacts`.

<br>

## Output file (result.csv)

![image](https://user-images.githubusercontent.com/83486603/155836697-80af34db-ea1c-4deb-9bee-4e6c6be16cb4.png)


<br>
The output file contains columns of input file along with two additional columns having **Topsis_score** and **Rank**
