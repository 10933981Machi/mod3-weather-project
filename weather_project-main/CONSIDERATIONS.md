# PySpark Migration Considerations

## Overview

To get the weather stats app running on PySpark I had to rewrite the core data processing logic. The original code was all pandas and ran on a single machine. PySpark distributes the work across a cluster, so I couldn't just use the same code. I ran it on a virtual cluster locally using `local[*]` mode which spins up a Spark worker for each CPU core.

---

## What I Had to Change

**SparkSession setup** — I needed to create a `SparkSession` as the entry point to Spark. I also ran into a Java version issue where PySpark 4.x is incompatible with Java 21+. The environment had Java 25 by default which broke everything. I had to detect and point to Java 17 before the JVM started.

**Loading the data** — Switched from `pd.read_csv()` to `spark.read.csv()` with schema inference. Spark reads the file across partitions in parallel instead of loading everything into memory on one machine.

**Rewriting the stats** — Pandas methods like `.mean()` and `.std()` don't work on Spark DataFrames. I replaced them with Spark's built-in functions (`F.mean()`, `F.stddev()`, etc.). Median was different too — Spark uses `approxQuantile()` since an exact median is expensive to compute on distributed data.

**Filtering and groupBy** — The pandas boolean indexing and `.groupby()` calls were replaced with Spark's `.filter()` and `.groupBy().agg()`. The logic is the same, just a different API.

**Spark SQL** — I added a SQL interface by registering the DataFrame as a temp view and running queries against it. This made it easy to write things like "top 10 hottest locations" in plain SQL.

**Type casting** — Some columns came back as strings when Spark inferred the schema. I had to explicitly cast them to `DoubleType` before doing any numeric operations.

**Removed ProcessPoolExecutor** — The previous phase used multiprocessing to parallelize stats across columns. With PySpark that's not needed — Spark handles parallelism internally, so I dropped that layer entirely.

