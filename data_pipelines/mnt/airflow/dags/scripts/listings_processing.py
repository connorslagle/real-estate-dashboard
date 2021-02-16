from os.path import expanduser, join, abspath
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, explode

warehouse_location = abspath('spark-warehouse')

# Initialize Spark Session
spark = SparkSession \
    .builder \
    .appName("listings processing") \
    .config("spark.sql.warehouse.dir", warehouse_location) \
    .enableHiveSupport() \
    .getOrCreate()

# Read the file forex_rates.json from the HDFS
df = spark.read.json('hdfs://namenode:9000/listings/listings_query_{}.json'.format(str(datetime.now().date())))

# Expand properties, make new df
df_listings = df.select(df.meta, explode(df.properties))

# Make temp table for SQL query
df_listings.createOrReplaceTempView('listings_table')

# Query listings_table for relevant data
df_to_hive = spark.sql('''
    SELECT
        col.`property_id`,
        current_date() AS query_date,
        meta.`tracking_params`.`city` AS query_city,
        meta.`tracking_params`.`state` AS query_state,
        col.`prop_type`,
        col.`address`.`line` AS address_line,
        col.`address`.`city` AS address_city,
        col.`address`.`postal_code` AS zip_code,
        col.`address`.`fips_code` AS fips_code,
        col.`address`.`lat` AS lat,
        col.`address`.`lon` AS lon,
        col.`address`.`neighborhood_name` as neighborhood,
        col.`price` AS listing_price,
        col.`baths`,
        col.`beds`,
        col.`building_size`.`size` AS building_size,
        col.`building_size`.`units` AS building_size_units,
        col.`lot_size`.`size` AS lot_size,
        col.`lot_size`.`units` AS lot_size_units,
        col.`last_update`,
        col.`rdc_web_url` AS url        
    FROM
        listings_table
''')

# Export the dataframe into the Hive table forex_rates
df_to_hive.write.mode("append").insertInto("listings")