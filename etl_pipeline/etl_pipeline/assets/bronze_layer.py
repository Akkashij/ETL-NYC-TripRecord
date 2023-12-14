from dagster import asset, AssetIn, Output, StaticPartitionsDefinition
import pandas as pd
from datetime import datetime, timedelta

def generate_weekly_dates(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    current_date = start_date
    while current_date < end_date:
        yield current_date.strftime("%Y-%m-%d")
        current_date += timedelta(weeks=1)
start_date_str = "2023-01-01"
end_date_str = "2023-07-01"

weekly_dates = list(generate_weekly_dates(start_date_str, end_date_str))
WEEKLY = StaticPartitionsDefinition(weekly_dates)


@asset(
    name="bronze_yellow_record",
    description="record of yellow taxi",
    io_manager_key="minio_io_manager",
    required_resource_keys={"mysql_io_manager"},
    key_prefix=["bronze", "trip_record"],
    compute_kind="MySQL",
    group_name="bronze",
    partitions_def=WEEKLY,
)
def bronze_yellow_record(context) -> Output[pd.DataFrame]:
    query = "SELECT * FROM yellow_record"
    try:
        partition = context.asset_partition_key_for_output()
        partition_by = "tpep_pickup_datetime"
        query += f" WHERE DATE({partition_by}) >= '{partition}' AND DATE({partition_by}) < DATE_ADD('{partition}', INTERVAL 1 WEEK);"
        context.log.info(f"Partition by {partition_by}: {partition} to 1 week later")
    except Exception:
        context.log.info("No partition key found")
    df_data = context.resources.mysql_io_manager.extract_data(query)
    context.log.info(f"Table extracted with shape: {df_data.shape}")

    return Output(
        df_data,
        metadata={
            "table": "yellow_record",
            "row_count": df_data.shape[0],
            "column_count": df_data.shape[1],
            "columns": str(df_data.columns),
        },
    )


@asset(
    name="bronze_green_record",
    description="record of green taxi",
    io_manager_key="minio_io_manager",
    required_resource_keys={"mysql_io_manager"},
    key_prefix=["bronze", "trip_record"],
    compute_kind="MySQL",
    group_name="bronze",
)
def bronze_green_record(context) -> Output[pd.DataFrame]:
    query = "SELECT * FROM green_record;"
    df_data = context.resources.mysql_io_manager.extract_data(query)
    context.log.info(f"Table extracted with shape: {df_data.shape}")

    return Output(
        df_data,
        metadata={
            "table": "green_record",
            "row_count": df_data.shape[0],
            "column_count": df_data.shape[1],
            "columns": str(df_data.columns),
        },
    )


@asset(
    name="bronze_fhv_record",
    description="record of fhv taxi",
    io_manager_key="minio_io_manager",
    required_resource_keys={"mysql_io_manager"},
    key_prefix=["bronze", "trip_record"],
    compute_kind="MySQL",
    group_name="bronze",
)
def bronze_fhv_record(context) -> Output[pd.DataFrame]:
    query = "SELECT * FROM fhv_record;"
    df_data = context.resources.mysql_io_manager.extract_data(query)
    context.log.info(f"Table extracted with shape: {df_data.shape}")

    return Output(
        df_data,
        metadata={
            "table": "fhv_record",
            "row_count": df_data.shape[0],
            "column_count": df_data.shape[1],
            "columns": str(df_data.columns),
        },
    )

