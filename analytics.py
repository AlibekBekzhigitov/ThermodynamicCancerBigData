import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator

# 1. Initialization of Apache Spark session with increased memory and column limit
spark = SparkSession.builder \
    .appName("ThermodynamicCancerAnalytics") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.csv.maxColumns", "40000") \
    .config("spark.sql.legacy.charVarcharAsString", "true") \
    .getOrCreate()

print("[*] Apache Spark session initialized successfully.")

# 2. Define paths to the data files (CCLE and Achilles datasets)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN_FILE = os.path.join(BASE_DIR, 'data', 'CCLE_gene_cn.csv')
ACHILLES_FILE = os.path.join(BASE_DIR, 'data', 'Achilles_gene_effect.csv')

# 3. Reading the data files (what we accidentally deleted)
df_cn = spark.read.option("maxColumns", 40000).csv(CN_FILE, header=True, inferSchema=True)
df_achilles = spark.read.option("maxColumns", 40000).csv(ACHILLES_FILE, header=True, inferSchema=True)

# 4. Standardizing ID columns (without hard-coded column names)
df_cn = df_cn.withColumnRenamed(df_cn.columns[0], "DepMap_ID")
df_achilles = df_achilles.withColumnRenamed(df_achilles.columns[0], "DepMap_ID")

print(f"[*] Loaded {df_cn.count()} cell line profiles from CCLE dataset.")
print(f"[*] Loaded {df_achilles.count()} cell line profiles from Achilles dataset.")

# 5. List of gene columns for both datasets, excluding the DepMap_ID column

# Renaming the first column to a standard name for easier joins
id_col_cn = df_cn.columns[0]
id_col_ach = df_achilles.columns[0]
df_cn = df_cn.withColumnRenamed(id_col_cn, "DepMap_ID")
df_achilles = df_achilles.withColumnRenamed(id_col_ach, "DepMap_ID")

print(f"[*] Loaded {df_cn.count()} cell line profiles.")

# List of gene columns for both datasets, excluding the DepMap_ID column
gene_columns = [c for c in df_cn.columns if c != "DepMap_ID"]
achilles_genes = [c for c in df_achilles.columns if c != "DepMap_ID"]

print("[*] Calculating genome entropy for each cell line...")

# 3. Native vectorization of the CNV matrix using Spark SQL functions
df_cn = df_cn.withColumn("genes_array", F.array([F.coalesce(F.col(f"`{c}`"), F.lit(0.0)) for c in gene_columns]))

# row_sum is calculated to normalize the gene copy number values for entropy calculation
df_cn = df_cn.withColumn("row_sum", F.aggregate("genes_array", F.lit(0.0), lambda acc, x: acc + x))

# 4. Calculation of genome entropy using a vectorized approach with Spark SQL functions
df_entropy = df_cn.withColumn(
    "Genome_Entropy",
    F.aggregate(
        "genes_array",
        F.lit(0.0),
        lambda acc, x: acc - ((x / (F.col("row_sum") + 1e-9)) * F.log((x / (F.col("row_sum") + 1e-9)) + 1e-9))
    )
).select("DepMap_ID", "Genome_Entropy")

print("[->] Entropy calculation completed successfully.")

# 5. Calculation of cell viability from Achilles matrix using a similar vectorized aggregator with escaping
print("[*] Calculating cell viability from Achilles matrix...")
df_achilles = df_achilles.withColumn("viability_array", F.array([F.coalesce(F.col(f"`{c}`"), F.lit(0.0)) for c in achilles_genes]))

df_viability = df_achilles.withColumn(
    "Cell_Viability",
    F.aggregate("viability_array", F.lit(0.0), lambda acc, x: acc + x) / len(achilles_genes)
).select("DepMap_ID", "Cell_Viability")

# Connection of the two datasets (entropy and viability) into a single dataset for machine learning
final_dataset = df_entropy.join(df_viability, on="DepMap_ID", how="inner").cache()

# Removing rows with null values to ensure a clean dataset for machine learning
final_dataset = final_dataset.na.drop()

print(f"[*] Clean dataset for ML: {final_dataset.count()} rows.")
final_dataset.show(5)

# 6. Machine learning in Spark MLlib (Search for nonlinear bifurcation point)
assembler = VectorAssembler(inputCols=["Genome_Entropy"], outputCol="features")
ml_data = assembler.transform(final_dataset).select("features", F.col("Cell_Viability").alias("label"))

train_data, test_data = ml_data.randomSplit([0.8, 0.2], seed=42)

# Using Gradient Boosting Trees (GBT)
gbt = GBTRegressor(featuresCol="features", labelCol="label", maxDepth=5, seed=42)
gbt_model = gbt.fit(train_data)

predictions = gbt_model.transform(test_data)

evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"\n[Result] Quality of the nonlinear physical model (RMSE) = {rmse:.4f}")

print("\n[*] Mathematical rules for model branching (Bifurcation points):")
print(gbt_model.toDebugString[:1000])

spark.stop()