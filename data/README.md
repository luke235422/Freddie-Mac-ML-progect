# Data

The raw data is **not** in this repository. The five quarters used here weigh
roughly 4 GB uncompressed (~800 MB zipped), and Freddie Mac distributes the
dataset under its own terms of use, which do not allow redistribution.

## Where to get it

1. Go to the Freddie Mac **Single-Family Loan-Level Dataset** page and create a
   free account: <https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset>
2. Accept the terms of use and open the download area for the **Standard**
   dataset (not Non-Standard, not the Sample).
3. Download the quarterly archives for the five quarters used by
   `final_model.ipynb`:

   | Vintage | Origination file | Performance file |
   |---|---|---|
   | 2022 Q4 | `orig_2022Q4.txt` | `perf_2022Q4.txt` |
   | 2023 Q2 | `orig_2023Q2.txt` | `perf_2023Q2.txt` |
   | 2023 Q3 | `orig_2023Q3.txt` | `perf_2023Q3.txt` |
   | 2023 Q4 | `orig_2023Q4.txt` | `perf_2023Q4.txt` |
   | 2024 Q1 | `orig_2024Q1.txt` | `perf_2024Q1.txt` |

## Expected folder layout

The notebook reads relative paths from the repository root, so unzip the
archives into this shape (the folder names are Freddie Mac's own):

```
Freddie-Mac-ML-project/
├── final_model.ipynb
├── historical_data_2022/
│   └── historical_data_2022Q4/
│       ├── orig_2022Q4.txt
│       └── perf_2022Q4.txt
├── historical_data_2023/
│   ├── historical_data_2023Q2/
│   │   ├── orig_2023Q2.txt
│   │   └── perf_2023Q2.txt
│   ├── historical_data_2023Q3/
│   │   └── ...
│   └── historical_data_2023Q4/
│       └── ...
└── historical_data_2024/
    └── historical_data_2024Q1/
        ├── orig_2024Q1.txt
        └── perf_2024Q1.txt
```

## File format

Both file types are pipe-delimited (`|`) with **no header row**, which is why the
notebook reads them with `header=None` and assigns column names explicitly:

```python
pd.read_csv(path, sep="|", header=None, low_memory=False)
```

Column orders come from the official layout in Freddie Mac's *General User
Guide*; they are defined in the first cells of `final_model.ipynb` as
`origination_columns` and `performance_columns`.

## Resource notes

- `perf_*.txt` files are the large ones (up to ~970 MB each for a single
  quarter). Loading all five quarters of performance data at once needs
  roughly 16 GB of RAM.
- The performance data is only used to build the target (delinquency status at
  loan age 20 months) and to audit which loans never reach that age. Once
  `target_df` is built, the performance frames can be dropped from memory.
