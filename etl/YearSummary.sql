/*

Example Load of the Year Summary data

*/

DROP TABLE IF EXISTS year_summary;

CREATE TABLE year_summary (
    last_name VARCHAR(255),
    BB integer,
    BBfrac float,
    BBz float,
    HR integer,
    HRfrac float,
    HRz float,
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
    Dfrac float,
    Dz float,
    H integer,
    K integer,
    Kfrac float,
    Kz float,
    team VARCHAR(100),
    S integer,
    Sfrac float,
    Sz float,
    T integer,
    Tfrac float,
    Tz float,
    SLG float,
    SLGz float,
    OBP float,
    OBPz float,
    OPS float,
    SH integer,
    Year date,
    AVG float,
    AVGz float,
    SF integer
);

COPY year_summary
FROM '/Users/patrickfisher/Documents/projects/bball_prj_games/YearSummary1980_2014.csv'
WITH CSV HEADER
DELIMITER AS ',';
