USE CBS;
GO

/*==============================================================
    Drop Existing Views
==============================================================*/

IF OBJECT_ID('dbo.vw_channel_transactions_summary', 'V') IS NOT NULL
    DROP VIEW dbo.vw_channel_transactions_summary;
GO

IF OBJECT_ID('dbo.vw_transaction_failure_rate', 'V') IS NOT NULL
    DROP VIEW dbo.vw_transaction_failure_rate;
GO

IF OBJECT_ID('dbo.vw_peak_transaction_hours', 'V') IS NOT NULL
    DROP VIEW dbo.vw_peak_transaction_hours;
GO

IF OBJECT_ID('dbo.vw_atm_performance', 'V') IS NOT NULL
    DROP VIEW dbo.vw_atm_performance;
GO

IF OBJECT_ID('dbo.vw_top_accounts', 'V') IS NOT NULL
    DROP VIEW dbo.vw_top_accounts;
GO

IF OBJECT_ID('dbo.vw_replication_lag_summary', 'V') IS NOT NULL
    DROP VIEW dbo.vw_replication_lag_summary;
GO

IF OBJECT_ID('dbo.vw_tnx_vs_lag', 'V') IS NOT NULL
    DROP VIEW dbo.vw_tnx_vs_lag;
GO

/*==============================================================
    1. Channel-wise Transaction Summary
==============================================================*/

CREATE VIEW dbo.vw_channel_transactions_summary
AS
SELECT
    channel,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_transaction_amount
FROM dbo.core_banking_transactions
GROUP BY channel;
GO


/*==============================================================
    2. Transaction Success / Failure Rate
==============================================================*/

CREATE VIEW dbo.vw_transaction_failure_rate
AS
SELECT
    tnx_status,
    COUNT(*) AS transaction_count,
    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(5,2)
    ) AS percentage
FROM dbo.core_banking_transactions
GROUP BY tnx_status;
GO


/*==============================================================
    3. Peak Transaction Hours
==============================================================*/

CREATE VIEW dbo.vw_peak_transaction_hours
AS
SELECT
    DATEPART(HOUR, tnx_timestamp) AS transaction_hour,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount
FROM dbo.core_banking_transactions
GROUP BY DATEPART(HOUR, tnx_timestamp);
GO


/*==============================================================
    4. ATM Performance
==============================================================*/

-- Fix 1: Case bug fix in existing view
CREATE VIEW dbo.vw_atm_performance
AS
SELECT
    atm_id,
    location,
    COUNT(*)                    AS total_transactions,
    AVG(response_time_ms)       AS avg_response_time_ms,
    SUM(withdrawal_amount)      AS total_withdrawal_amount,
    SUM(CASE WHEN tnx_status = 'FAILED'   -- was 'Failed', now 'FAILED'
             THEN 1 ELSE 0 END) AS failed_transactions
FROM dbo.atm_logs
GROUP BY atm_id, location;
GO


-- Fix 2: New view that uses the linkage you just built
CREATE VIEW dbo.vw_atm_transaction_details
AS
SELECT
    t.tnx_id,
    t.account_id,
    t.amount,
    t.tnx_status,
    t.tnx_timestamp,
    t.atm_id,
    a.location,
    a.avg_response_time_ms
FROM dbo.core_banking_transactions t
INNER JOIN (
    -- Aggregate atm_logs to one row per ATM
    SELECT
        atm_id,
        location,
        AVG(response_time_ms) AS avg_response_time_ms,
        COUNT(*)              AS total_atm_transactions
    FROM dbo.atm_logs
    GROUP BY atm_id, location
) a ON t.atm_id = a.atm_id
WHERE t.channel = 'ATM';
GO

/*==============================================================
    5. Top Accounts
==============================================================*/

CREATE VIEW dbo.vw_top_accounts
AS
SELECT TOP (10)
    account_id,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount
FROM dbo.core_banking_transactions
GROUP BY account_id
ORDER BY total_amount DESC;
GO


/*==============================================================
    6. Replication Lag Summary
==============================================================*/

CREATE VIEW dbo.vw_replication_lag_summary
AS
SELECT
    environment,
    AVG(extract_lag_sec) AS avg_extract_lag,
    AVG(replicat_lag_sec) AS avg_replicat_lag,
    AVG(trail_file_size_mb) AS avg_trail_file_size_mb,
    AVG(log_read_rate_mb) AS avg_log_read_rate_mb
FROM dbo.replication_metrics
GROUP BY environment;
GO


/*==============================================================
    7. Transaction Volume vs Replication Lag
==============================================================*/

CREATE VIEW dbo.vw_tnx_vs_lag
AS
SELECT
    DATEPART(HOUR, t.tnx_timestamp) AS transaction_hour,

    COUNT(*) AS transaction_volume,

    AVG(r.extract_lag_sec) AS avg_extract_lag,

    AVG(r.replicat_lag_sec) AS avg_replicat_lag

FROM dbo.core_banking_transactions t

INNER JOIN dbo.replication_metrics r

ON DATEPART(HOUR, t.tnx_timestamp)
=
DATEPART(HOUR, r.metric_timestamp)

GROUP BY
DATEPART(HOUR, t.tnx_timestamp);
GO