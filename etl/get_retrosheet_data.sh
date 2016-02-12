#!/bin/sh

# Extract RetroSheet Data

ETL_LOG=etl.log
retrosheet_dir=./retrosheet_data

for year in $(seq 1980 1 1982)
do
    echo "Downloading year: ${year}"
    wget http://www.retrosheet.org/events/${year}eve.zip -P $retrosheet_dir 2>&1 | tee -a $ETL_LOG
    echo "Extracting year: ${year}" 
    unzip ${retrosheet_dir}/${year}eve.zip -d $retrosheet_dir 2>&1 | tee -a $ETL_LOG
    echo "Cleaning up: ${year}"
    rm ${retrosheet_dir}/*.ROS
    rm ${retrosheet_dir}/TEAM*
    rm ${retrosheet_dir}/*.zip
done
