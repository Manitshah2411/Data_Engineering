CREATE SCHEMA IF NOT EXISTS meta;

-- This table stores just the configurations like which table and schema, created and updated at etc.
CREATE TABLE IF NOT EXISTS meta.config (
    pipeline_name           VARCHAR(100) PRIMARY KEY,
    target_schema           VARCHAR(50)  NOT NULL,
    target_table            VARCHAR(50)  NOT NULL,

    load_type               VARCHAR(20)  NOT NULL
        CHECK (load_type IN ('FULL', 'INCREMENTAL', 'UPSERT')),

    watermark_column        VARCHAR(50),
    truncate_before_load    BOOLEAN NOT NULL DEFAULT FALSE,
    allow_updates           BOOLEAN NOT NULL DEFAULT FALSE,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,

    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- This table is the actual data and grows after each run of a pipeline.
CREATE TABLE IF NOT EXISTS meta.etl_runs (
    run_id              BIGSERIAL PRIMARY KEY,
    pipeline_name       VARCHAR(100) NOT NULL,

    status              VARCHAR(20) NOT NULL
        CHECK (status IN ('IN_PROGRESS', 'SUCCESS', 'FAILED')),

    start_time          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time            TIMESTAMP,

    watermark_used      TIMESTAMP,
    rows_processed      INTEGER,

    error_message       TEXT,

    CONSTRAINT fk_pipeline
        FOREIGN KEY (pipeline_name)
        REFERENCES meta.config(pipeline_name)
);

CREATE UNIQUE INDEX uq_pipeline_running
ON meta.etl_runs (pipeline_name)
WHERE status = 'IN_PROGRESS';

