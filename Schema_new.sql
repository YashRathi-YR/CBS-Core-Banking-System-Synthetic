/*==============================================================
    Core Banking Data Analytics
    Database & Schema Creation
==============================================================*/

-- Create the database only if it doesn't already exist
IF DB_ID('CBS') IS NULL
BEGIN
    CREATE DATABASE CBS;
END
GO

-- Switch to the CBS database
USE CBS;
GO

/*==============================================================
    Drop Existing Tables (Safe to Re-run)
==============================================================*/

IF OBJECT_ID('dbo.replication_metrics', 'U') IS NOT NULL
    DROP TABLE dbo.replication_metrics;
GO

IF OBJECT_ID('dbo.interest_logs', 'U') IS NOT NULL
    DROP TABLE dbo.interest_logs;
GO

IF OBJECT_ID('dbo.atm_logs', 'U') IS NOT NULL
    DROP TABLE dbo.atm_logs;
GO

IF OBJECT_ID('dbo.core_banking_transactions', 'U') IS NOT NULL
    DROP TABLE dbo.core_banking_transactions;
GO

/*==============================================================
    CORE BANKING TRANSACTIONS
==============================================================*/

CREATE TABLE dbo.core_banking_transactions
(
    tnx_id          BIGINT NOT NULL,
    account_id      BIGINT NOT NULL,
    branch_id       INT NOT NULL,
    tnx_type        VARCHAR(30) NULL,
    channel         VARCHAR(30) NULL,
    amount          DECIMAL(18,2) NULL,
    tnx_status      VARCHAR(20) NULL,
    tnx_timestamp   DATETIME NULL,
    atm_id          INT NULL,        -- ADD THIS LINE

    CONSTRAINT PK_core_banking_transactions
        PRIMARY KEY CLUSTERED (tnx_id)
);
GO

/*==============================================================
    ATM LOGS
==============================================================*/

CREATE TABLE dbo.atm_logs
(
    log_id              BIGINT IDENTITY(1,1) NOT NULL,  -- auto-increment PK
    atm_id              INT NOT NULL,                    -- which ATM
    location            VARCHAR(100) NULL,               -- fixed per ATM
    withdrawal_amount   DECIMAL(18,2) NULL,
    tnx_status          VARCHAR(20) NULL,
    response_time_ms    INT NULL,
    [timestamp]         DATETIME NULL,

    CONSTRAINT PK_atm_logs
        PRIMARY KEY CLUSTERED (log_id)                  -- PK on log_id, not atm_id
);
GO

/*==============================================================
    INTEREST LOGS
==============================================================*/

CREATE TABLE dbo.interest_logs
(
    account_id BIGINT NULL,
    interest_rate DECIMAL(5,2) NULL,
    daily_balance DECIMAL(18,2) NULL,
    interest_amount DECIMAL(18,2) NULL,
    accrual_date DATE NULL
);
GO

/*==============================================================
    REPLICATION METRICS
==============================================================*/

CREATE TABLE dbo.replication_metrics
(
    environment VARCHAR(10) NULL,
    extract_lag_sec DECIMAL(10,2) NULL,
    replicat_lag_sec DECIMAL(10,2) NULL,
    trail_file_size_mb DECIMAL(10,2) NULL,
    log_read_rate_mb DECIMAL(10,2) NULL,
    metric_timestamp DATETIME NULL
);
GO