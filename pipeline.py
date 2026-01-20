from dagster import op, graph, job, ScheduleDefinition, Definitions, sensor, RunFailureSensorContext, SkipReason
import subprocess
import os

# -------------------------
# OP 1: Scrape Telegram Data
# -------------------------
@op
def scrape_telegram_data(context):
    context.log.info("Running Telegram scraper...")
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    context.log.info("Scraper completed successfully.")
    return "done"  # dummy output for chaining

# -------------------------
# OP 2: Load Raw Data to Postgres
# -------------------------
@op
def load_raw_to_postgres(context, prev: str):
    context.log.info("Loading raw data to Postgres...")
    result = subprocess.run(["python", "scripts/load_raw_to_postgres.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Load failed: {result.stderr}")
    context.log.info("Raw data load completed successfully.")
    return "done"

# -------------------------
# OP 3: Run DBT Transformations
# -------------------------
@op
def run_dbt_transformations(context, prev: str):
    context.log.info("Running DBT transformations...")
    original_dir = os.getcwd()
    os.chdir("medical_warehouse")
    result = subprocess.run(["dbt", "run"], capture_output=True, text=True)
    os.chdir(original_dir)
    if result.returncode != 0:
        raise Exception(f"DBT failed: {result.stderr}")
    context.log.info("DBT transformations completed successfully.")
    return "done"

# -------------------------
# OP 4: Run YOLO Enrichment
# -------------------------
@op
def run_yolo_enrichment(context, prev: str):
    context.log.info("Running YOLO object detection...")
    result = subprocess.run(["python", "src/yolo_detect.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLO failed: {result.stderr}")
    context.log.info("YOLO enrichment completed successfully.")
    return "done"

# -------------------------
# GRAPH: Medical Telegram Pipeline
# -------------------------
@graph
def medical_telegram_pipeline():
    # Chaining ops sequentially
    scrape = scrape_telegram_data()
    load = load_raw_to_postgres(scrape)
    dbt = run_dbt_transformations(load)
    yolo = run_yolo_enrichment(dbt)

# Convert graph to job
pipeline_job = medical_telegram_pipeline.to_job(name="medical_telegram_pipeline")

# -------------------------
# Daily Schedule at 2 AM UTC
# -------------------------
daily_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="0 2 * * *",  # 2 AM UTC daily
    name="daily_medical_pipeline"
)

# -------------------------
# Failure Sensor (basic log)
# -------------------------
@sensor(job=pipeline_job)
def pipeline_failure_sensor(context: RunFailureSensorContext):
    context.log.error(f"Pipeline failed: {context.failure_event.message}")
    return SkipReason("Pipeline failure detected")

# -------------------------
# Dagster Definitions
# -------------------------
defs = Definitions(
    jobs=[pipeline_job],
    schedules=[daily_schedule],
    sensors=[pipeline_failure_sensor]
)
