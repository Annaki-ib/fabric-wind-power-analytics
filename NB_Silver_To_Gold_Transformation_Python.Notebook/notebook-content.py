# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "485070a6-d495-48fc-93f3-713d62e6c282",
# META       "default_lakehouse_name": "LH_Wind_Power_Silver",
# META       "default_lakehouse_workspace_id": "f6af98c0-78cd-4c2c-980e-b223713812d8",
# META       "known_lakehouses": [
# META         {
# META           "id": "485070a6-d495-48fc-93f3-713d62e6c282"
# META         },
# META         {
# META           "id": "a5f63e30-f6f1-4750-8d74-c26fa44a9150"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Path to the table in the Silver Lakehouse
silver_table_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Silver.Lakehouse/Tables/dbo/wind_power"
# Load the table into a DataFrame
df = spark.read.format("delta").load(silver_table_path)
# Display df
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Create the Date Dimension Table
date_dim = (
  df.select(
    "date",
    "day",
    "month",
    "quarter",
    "year",
  )
  .distinct()
  .withColumnRenamed("date", "date_id")
)
# Display date_dim
display(date_dim)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Create the Time Dimension Table
time_dim = (
   df.select(
     "time",
     "hour_of_day",
     "minute_of_hour",
     "second_of_minute",
     "time_period",
    )
    .distinct()
    .withColumnRenamed("time", "time_id")
)
# Display time_dim
display(time_dim)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Create the Turbine Dimension Table
turbine_dim = (
  df.select(
    "turbine_name",
    "capacity",
    "location_name",
    "latitude",
    "longitude",
    "region",
  )
  .distinct()
  .withColumn(
     "turbine_id",
      row_number().over(Window.orderBy("turbine_name", "capacity",
     "location_name", "latitude", "longitude", "region")),
   )
)
# Display turbine_dim
display(turbine_dim)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Create the Operational Status Dimension Table
operational_status_dim = (
df.select(
"status",
"responsible_department",
)
.distinct()
.withColumn(
"status_id",
row_number().over(Window.orderBy("status", "responsible_department")),
)
)
# Display operational_status_dim
display(operational_status_dim)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Join the dimension tables to the original DataFrame
df = (
df.join(
turbine_dim,
["turbine_name", "capacity", "location_name", "latitude", "longitude",
"region"],
"left",
)
.join(
operational_status_dim,
["status", "responsible_department"],
"left",
)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Create the Fact table
fact_table = (
df.select(
"production_id",
"date",
"time",
"turbine_id",
"status_id",
"wind_direction",
"wind_speed",
"energy_produced",
)
.withColumnRenamed("date", "date_id")
.withColumnRenamed("time", "time_id")
)
# Display fact_table
display(fact_table)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Paths to the Gold tables
gold_date_dim_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Gold.Lakehouse/Tables/dbo/dim_date"
gold_time_dim_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Gold.Lakehouse/Tables/dbo/dim_time"
gold_turbine_dim_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Gold.Lakehouse/Tables/dbo/dim_turbine"
gold_operational_status_dim_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Gold.Lakehouse/Tables/dbo/dim_operational_status"
gold_fact_table_path = "abfss://WindPowerAnalytics_annaki@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Gold.Lakehouse/Tables/dbo/FactWindPower"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Save the tables in the Gold Lakehouse
date_dim.write.format("delta").mode("overwrite").save(gold_date_dim_path)
time_dim.write.format("delta").mode("overwrite").save(gold_time_dim_path)
turbine_dim.write.format("delta").mode("overwrite").save(gold_turbine_dim_path)
operational_status_dim.write.format("delta").mode("overwrite").save(gold_operational_status_dim_path)
fact_table.write.format("delta").mode("overwrite").save(gold_fact_table_path)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
