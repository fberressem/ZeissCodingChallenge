import argparse
import utils
from datetime import timedelta

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-F", "--filename", type=str, default="sample_temperature_data_for_coding_challenge.csv",
                    help="Filename to read data from")
parser.add_argument("-O", "--output", type=str, default="temperature.csv",help="Output to save interpolated data to")
parser.add_argument("-S", "--spline_order", type=int, default=1,help="Order of spline for interpolation")
parser.add_argument("-T", "--timedelta", type=int, default=60,help="Timedelta for interpolation in minutes")
parser.add_argument("-M", "--max_interval", type=int, default=None,help="Maximum time-interval in minutes." \
                    "Time-intervals larger than this value are interpolated linearly.")
parser.add_argument("-P", "--plot", default=False, action="store_true",help="Plot temperatures if enabled")
parser.add_argument("-K", "--keep_old", default=False, action="store_true",
                    help="Keep old data during interpolation if enabled")
parser.add_argument("-I", "--interpolation_mode", choices=["interp1d", "bspline", "univ"], default="interp1d",
                    help="Method to use for interpolation")

args = parser.parse_args()

assert args.spline_order >= 0, "Order of spline has to be >= 0"

# Read data to dict
data = utils.readData(args.filename)

# Cast and convert values in data
data["temperature"] = utils.cast(data["temperature"], float)
data["datetime"] = utils.convertDatetime(data["datetime"])

# Split data into data for cooling_temperature and heating_temperature
data_split = utils.splitProperties(data = data, prop = "property_name", check_duplicates = ["datetime"])

# If plotting is enabled, plot original data in separate plots for different temperature-types
if args.plot:
    import matplotlib.pyplot as plt
    
    keys = sorted(list(data_split.keys()))    
        
    fig,axes = plt.subplots(2,1)
    
    for i, k in enumerate(keys):
        axes[i].set_title(k)    
        axes[i].plot(data_split[k]["datetime"], data_split[k]["temperature"], label="Original data")


# For all temperature types interpolate data and adjust axes which were not interpolated
for k in data_split.keys():
    # Calculate interpolation and interpolated indices
    x,y, inds_interp = utils.interpolate(x_vals = data_split[k]["datetime"], y_vals = data_split[k]["temperature"],
                            order = args.spline_order, delta = timedelta(minutes=args.timedelta),
                            keep_old=args.keep_old, interpolation_mode = args.interpolation_mode,
                            max_interval = args.max_interval)
    
    # Set datetime and temperature to interpolated values
    data_split[k]["datetime"] = x
    data_split[k]["temperature"] = y
    
    # Pad property_name and source_id to same length of datetime and temperature
    utils.padData(data_split[k])
    utils.padData(data_split[k], pad_len_of = "property_name")
    
    # For all indices which were interpolated set source_id to interpolation
    for i in inds_interp:
        data_split[k]["source_id"][i] = "interpolation"
        
    # Write CSV-file for this property. Does not fulfill "original" format for datetimes
    utils.writeCSV(k + ".csv", data_split[k])        
    
# Flatten and sort the dict
data = utils.flattenDict(data_split = data_split, property_name = "property_name", sort_by = "datetime")

# Convert datetime to string fulfilling the "original" format 
data["datetime"] = utils.datetimeToString(data["datetime"])

# Write whole data to CSV-file
utils.writeCSV(args.output, data)

# If plotting is enabled, plot interpolated data in same plot as original data
if args.plot:
    for i, k in enumerate(keys):
        axes[i].set_title(k)    
        axes[i].plot(data_split[k]["datetime"], data_split[k]["temperature"], label="Interpolated data", linestyle="dashed")

        axes[i].legend(loc=0)
        
    plt.show()

