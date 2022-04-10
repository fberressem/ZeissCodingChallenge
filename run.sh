#!/bin/bash -e
set -euo pipefail
IFS=$'\n\t'

filename="sample_temperature_data_for_coding_challenge.csv"
output="temperature.csv"
spline_order="1"
timedelta="60"
max_interval="10000000000"  # more than 19000 years should be sufficient
interpolation_mode="interp1d"
keep_old="0"
plot="0"
while [[ "$#" -gt 0 ]]; do
    key=$1
    
    case $key in
        -F|--filename)
            filename="$2"
            shift # past argument
            shift # past value
            ;;
        -O|--output)
            output="$2"
            shift # past argument
            shift # past value
            ;;
    	-S|--spline_order)
	        spline_order="$2"
	        shift # past argument
            shift # past value
	        ;;
	    -T|--timedelta)
	        timedelta="$2"
	        shift # past argument
            shift # past value
	        ;;
	    -M|--max_interval)
	        max_interval="$2"
	        shift # past argument
            shift # past value
	        ;;
	    -I|--interpolation_mode)
	        interpolation_mode="$2"
	        shift # past argument
            shift # past value
	        ;;
	    -K|--keep_old)
	        keep_old="1"
	        shift # past argument
	        ;;
	    -P|--plot)
	        plot="1"
	        shift # past argument
	        ;;
    	*)
            echo "Option '$key' not implemented"
            exit
    esac
done

source Venv/bin/activate

if [ "$keep_old" -eq "1" ]
    then
        if [ "$plot" -eq "1" ]
            then
                python3 main.py -F $filename -O $output -S $spline_order -T $timedelta -M $max_interval -I $interpolation_mode -K -P
            else
                python3 main.py -F $filename -O $output -S $spline_order -T $timedelta -M $max_interval -I $interpolation_mode -K
        fi
    else
        if [ "$plot" -eq "1" ]
            then
                python3 main.py -F $filename -O $output -S $spline_order -T $timedelta -M $max_interval -I $interpolation_mode -P
            else
                python3 main.py -F $filename -O $output -S $spline_order -T $timedelta -M $max_interval -I $interpolation_mode
        fi
fi      

deactivate

