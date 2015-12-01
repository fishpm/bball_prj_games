/*

Example Load of the Year Summary data

*/

DROP TABLE IF EXISTS year_summary;

CREATE TABLE year_summary (
    last_name VARCHAR(255),
    BB integer,
    HR integer,
    HP integer,
    FC integer,
    id VARCHAR(255),
    first_name VARCHAR(50),
    ROE integer,
    PA integer,
    TB integer,
    IBB integer,
    AB integer,
    D integer,
    H integer,
    K integer,
    team VARCHAR(100),
    S integer,
    T integer,
    SLG float,
    OBP float,
    OPS float,
    SH float,
    Year date,
    AVG float,
    SF integer
)

COPY year_summary
FROM 'YearSummary1980_2014.csv'
WITH CSV HEADER
DELIMITER AS ',';
