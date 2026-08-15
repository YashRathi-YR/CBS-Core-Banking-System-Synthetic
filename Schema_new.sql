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
CORE BANKING TRANSACTIONS
==============================================================*/
IF OBJECT_ID('dbo.core_banking_transactions', 'U') IS NULL
BEGIN
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
        atm_id          INT NULL,

        CONSTRAINT PK_core_banking_transactions
            PRIMARY KEY CLUSTERED (tnx_id)
    );
END
GO

/*==============================================================
ATM LOGS
==============================================================*/
IF OBJECT_ID('dbo.atm_logs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.atm_logs
    (
        log_id              BIGINT IDENTITY(1,1) NOT NULL,
        tnx_id              BIGINT NOT NULL,
        atm_id              INT NOT NULL,
        location            VARCHAR(100) NULL,
        withdrawal_amount   DECIMAL(18,2) NULL,
        tnx_status          VARCHAR(20) NULL,
        response_time_ms    INT NULL,
        [timestamp]         DATETIME NULL,

        CONSTRAINT PK_atm_logs
            PRIMARY KEY CLUSTERED (log_id),

        CONSTRAINT FK_atm_logs_transactions
            FOREIGN KEY (tnx_id)
            REFERENCES dbo.core_banking_transactions(tnx_id)
    );
END
GO

/*==============================================================
INTEREST LOGS
==============================================================*/
IF OBJECT_ID('dbo.interest_logs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.interest_logs
    (
        account_id       BIGINT NULL,
        interest_rate    DECIMAL(5,2) NULL,
        daily_balance    DECIMAL(18,2) NULL,
        interest_amount  DECIMAL(18,2) NULL,
        accrual_date     DATE NULL
    );
END
GO

/*==============================================================
REPLICATION METRICS
==============================================================*/
IF OBJECT_ID('dbo.replication_metrics', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.replication_metrics
    (
        environment         VARCHAR(10) NULL,
        extract_lag_sec     DECIMAL(10,2) NULL,
        replicat_lag_sec    DECIMAL(10,2) NULL,
        trail_file_size_mb  DECIMAL(10,2) NULL,
        log_read_rate_mb    DECIMAL(10,2) NULL,
        metric_timestamp    DATETIME NULL
    );
END
GO