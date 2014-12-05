source ./hadoop.cfg
hadoop fs -mkdir VDV
	hadoop fs -mkdir VDV/Last7Days
	hadoop fs -mkdir VDV/TodaysLoad
	hadoop fs -mkdir VDV/Targets
	hadoop fs -mkdir VDV/RawTargets
	hadoop fs -mkdir VDV/RawTargets/Vehicle
	hadoop fs -mkdir VDV/RawTargets/Driver
	hadoop fs -mkdir VDV/Actuals
	hadoop fs -mkdir VDV/OfficeHours
	hadoop fs -copyFromLocal ./Last7DaysAggDummy VDV/Last7Days
	echo "<<<-----XXXX----  Copying Today's Data from S3 ----XXXX----->>>";
#hadoop fs -copyFromLocal ./KPIVehicleTargets.csv VDV/RawTargets/Vehicle/
#hadoop fs -copyFromLocal ./KPIDriverTargets.csv VDV/RawTargets/Driver/
#hadoop fs -copyFromLocal ./OwnerOfficeHours.csv VDV/OfficeHours/
hadoop distcp s3n://$awsKey:$awsSecretKey@$bucket/$region/KPIVehicleTargets.csv VDV/RawTargets/Vehicle/
hadoop distcp s3n://$awsKey:$awsSecretKey@$bucket/$region/KPIDriverTargets.csv VDV/RawTargets/Driver/
hadoop distcp s3n://$awsKey:$awsSecretKey@$bucket/$region/OwnerOfficeHours.csv VDV/OfficeHours/
echo "<<<-----XXXX----  Starting VDV(PIG) process  ----XXXX----->>>";
	echo "<<<-----XXXX----  Running Current Data script  ----XXXX----->>>";
	pig CurrentData.pig
	if hadoop fs -test -d "VDV/Actuals/JustAgg"
	then
		echo "<<<-----XXXX----  Running Current Target script  ----XXXX----->>>";	
		pig CurrentTargets.pig
		pig CurrentDriverTargets.pig
		if hadoop fs -test -d "VDV/Targets/JustTargets"
		then
			echo "<<<-----XXXX----  Running Merge Actuals and Target script  ----XXXX----->>>";
			pig MergeActualsAndTargets.pig
			if hadoop fs -test -d "VDV/TodaysLoad/CurrData"
			then
				echo "<<<-----XXXX----  Consolidating with Late Arrival Data  ----XXXX----->>>";
				pig Last7DayAggregate.pig
				if hadoop fs -test -d "VDV/AggregateData.csv"
				then
					echo "<<<-----XXXX----  VDV scripts completed Successfully  ----XXXX----->>>";
				else
					echo "<<<-----XXXX----  Consolidating Todays Data with Late Arrival Aggregates failed!!!  ----XXXX----->>>";
					exit
				fi
			else
				echo "<<<-----XXXX----  Merge Actuals and Target script failed!!  ----XXXX----->>>";
				exit
			fi
		else
			echo "<<<-----XXXX----  Current Target script failed!!!  ----XXXX----->>>";
			exit
		fi
	else
		echo "<<<-----XXXX----  Current Data script failed!!!  ----XXXX----->>>";
		exit
	fi
if hadoop fs -test -e "VDV/Last7DaysAgg"
then
	echo "<<<-----XXXX----  Cleaning up Last7DaysAggregate  ----XXXX----->>>";
	hadoop fs -rmr VDV/Last7Days/*
	hadoop fs -mv VDV/Last7DaysAgg/part* VDV/Last7Days
	hadoop fs -rmr VDV/Last7DaysAgg
	hadoop fs -expunge
else 
	echo "<<<-----XXXX----  Last 7 Days storage failed!!! ----XXXX----->>>";
fi
