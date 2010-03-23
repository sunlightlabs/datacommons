SELECT rrb.RecipientReportsBundleID, r.StateCode, r.RState
FROM RecipientReportsBundle rrb
    JOIN Recipients r
    ON rrb.RecipientID = r.RecipientID
INTO OUTFILE '/tmp/nimsp_recipientstate.csv'
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n';

SELECT * FROM Contributions
INTO OUTFILE '/tmp/nimsp_contributions.csv'
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n';

SELECT RecipientReportsBundleID, MIN(Date) AS MinDate, MAX(Date) AS MaxDate
FROM Contributions
WHERE Date IS NOT NULL
GROUP BY RecipientReportsBundleID
INTO OUTFILE '/tmp/nimsp_bundledates.csv'
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n';