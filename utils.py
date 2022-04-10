import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Tuple, List, Set, Dict, Union
from scipy.interpolate import interp1d, BSpline, UnivariateSpline

def readData(filename: str = "sample_temperature_data_for_coding_challenge.csv",
             exclude_cols: Union[List,Tuple,Set] = []):
    """
    Reads data from csv-file to dictionary, where keys are given by first line

    Args:
        filename: Name of the file
        exclude_cols: List of columns to ignore
        
    Returns:
        data: Dictionary containing the read data with keys corresponding to first line 
    """ 
    
    structure = None
    inds = None
    data = defaultdict(list)
    with open(filename, "r") as f:
        for line in f:
            ls = line.strip().split(",")
            if structure is None:
                # Save the structure; allows to have a mapping from column-index
                # to logged quantity 
                structure = ls
                # Saving indices which are to be read
                inds = [i for i in range(len(ls)) if i not in exclude_cols]
            else:
                # Loop only over relevant indices
                for i in inds:
                    data[structure[i]].append(ls[i].strip())
    return data

def convertDatetime(l: List, pattern: str = "%Y-%m-%dT%H:%M:%S.%f%z"):
    """
    Converts list of strings to datetime according to pattern

    Args:
        l: List of strings representing datetimes
        pattern: Pattern in which to parse strings to datetime
        
    Returns:
        List containing converted datetimes
    """ 

    return list(map(lambda x : datetime.strptime(x, pattern), l))
    
def datetimeToString(l: List, pattern: str = "%Y-%m-%dT%H:%M:%S.%f%z"):
    """
    Converts list of datetimes to strings according to pattern

    Args:
        l: List of datetimes
        pattern: Pattern in which to output datetime as strings
        
    Returns:
        List containing converted datetimes
    """ 
    
    # Unfortunately, replace has to be done manually, as datetime works in microseconds in
    # Python, while data is in milliseconds
    return list(map(lambda x : x.strftime(pattern).replace(".000000", ".000"), l))

def cast(l, type_):
    """
    Applies typecast to all elements from l

    Args:
        l: List of elements to cast
        type_: Typecast-function to apply. Example: 'float', 'int', ... 
    
    Returns:
        List containing typecasted elements
    """
        
    return [type_(e) for e in l]


def splitProperties(data: Dict, prop: str = "property_name", check_duplicates: List = ["datetime"]):
    """
    Splits data into dictionaries according to property given by prop

    Args:
        data: Dictionary, with values being lists
        prop: Property to split data by
        check_duplicates: List of properties for which to check if there are duplicates after splitting.
                          Raises DuplicateException.
        
    Returns:
        data_split: Dictionary of dictionaries, split according to values of prop
    """
    
    class DuplicateException(Exception):
        pass    
    
    # Extract all values of prop for latter usage as mask
    prop_vals = data[prop]
    # Identify all the different values for property prop
    prop_vals_set = sorted(list(set(data[prop])))
    # Initialize defaultdict for all the different values for property prop
    data_split = {v:{} for v in prop_vals}
    # For every property
    for k in data.keys():
        # For all the different values for property prop
        for v in prop_vals_set:
            # Save the data for which data[prop] == val
            data_split[v][k] = [v_ for v_, p in zip(data[k], prop_vals) if p == v]
            if k in check_duplicates:
                if len(data_split[v][k]) != len(set(data_split[v][k])):
                    raise DuplicateException(f"Found duplicates for split-property '{v}' for key '{k}'")
    
    return data_split

def identifyTimeIntervals(times: List, max_interval = None):
    """
    Identify time-intervals in which consecutive values are not separated by more than 'max_interval'

    Args:
        times: List of times
        max_interval: Maximum allowed distance between consecutive times
        
    Returns:
        intervals: List of start end end times of consecutive values
    """
    
    if max_interval is None:
        return [[times[0], times[-1]]]
    
    else:
        mi = timedelta(minutes=max_interval)

    # Initialize start-value and interval-list
    start = None
    intervals = []
    for i in range(1, len(times)):
        # If consecutive elemnts are not separated by more than max_interval 
        if times[i] - times[i-1] <= mi:
            # If start is None, i.e. no start-value for a cluster has been found, set start to time at i-1 
            if start is None:
                start = times[i-1]
            # If start is not None, i.e. current element is part of the current cluster, continue
            else:
                continue
        # If consecutive elemnts are separated by more than max_interval 
        else:
            # If we currently have a cluster, add interval to list of valid intevrals and reset start 
            if start is not None:
                intervals.append([start, times[i-1]])
                start = None
    
    # If all elements are valid, add only one interval, ranging from start to end 
    if start == times[0]:
        intervals = [[times[0], times[-1]]]
        
    
    return intervals

def interpolate(x_vals: List, y_vals: List, order: int = 0, delta = timedelta(minutes=1),
                keep_old: bool = True, interpolation_mode: str = "interp1d",
                max_interval = None):
    """
    Interpolate the data with interpolation axis being given by index_prop with order and spacing
    as given by parameters. If max_interval is not None, interpolation region is split into
    chunks of consecutive times with data in between these chunks being linearly interpolated.
    
    Arguments:
        x_vals: Interpolation axis
        y_vals: Values to be interpolated
        order: Order of interpolation spline. 0 replicates last value
        delta: Desired spacing between datapoints along interpolation axis 
        keep_old: Keep old data during interpolation if enabled
        interpolation_mode: Method of interpolation to use. Currently, choose from ['bspline', 'interp1d', 'univ']
        max_interval: Maximum allowed timeinterval in minutes between consecutive times. For larger distances, data
                      is interpolated linearly, instead of with splines of higher order.
    
    Returns:
        x_interp: interpolated x-axis
        y_interp: interpolated y-values
        inds_interp: list of indices, which were interpolated (for use in setting of source)
    """
    
    assert interpolation_mode in ['bspline', 'interp1d', 'univ'], f"interpolation_mode has to be chosen from ['bspline', 'interp1d', 'univ']"
    

    # If interpolation axis is of type datetime, convert to unixtime for interpolation
    if isinstance(x_vals[0], datetime):
        # Create x-values for evaluation of interpolation spline
        x_interp = [x_vals[0]]
        while x_interp[-1] + delta <= x_vals[-1]:
            x_interp.append(x_interp[-1] + delta)
        
        # If old values should be kept, add old values, remove duplicates via set and sort
        if keep_old:
            x_interp = sorted(list(set(x_interp + x_vals)))

        # Allocate array for results of interpolation
        y_interp = np.zeros(len(x_interp))

        # Convert original values to unixtime for interpolation
        x_unix = np.array([x_.timestamp() for x_ in x_vals])
        # Convert datapoints for which interpolation should be evaluated to unixtime
        x_interp_unix = np.array([x_.timestamp() for x_ in x_interp])
        
        # Convert original values to NumPy-array for indexing
        y_vals = np.array(y_vals)
        
        # Extract all consecutive time intervals (as given by max_interval) which will be
        # interpolated via spline
        time_intervals = identifyTimeIntervals(x_vals, max_interval = max_interval)
        # Initialize all indices of x_vals as not used for spline yet
        valid_inds = np.zeros(len(x_vals), dtype=bool)
        # Initialize all indices of x_interp as not evaluated using spline yet
        valid_inds_interp = np.zeros(len(x_interp), dtype=bool)
        for t in time_intervals:
            try:
                # Determine all indices of x_vals in current time interval
                inds = np.logical_and(np.array(x_vals) >= t[0], np.array(x_vals) <= t[-1])
                
                # Interpolate according to chosen method
                if interpolation_mode == "bspline":
                    func = BSpline(x_unix[inds], y_vals[inds], k = order)
                elif interpolation_mode == "interp1d":
                    func = interp1d(x_unix[inds], y_vals[inds], kind=order)
                elif interpolation_mode == "univ":
                    func = UnivariateSpline(x_unix[inds], y_vals[inds], k=order)
                
                # Determine all indices of x_interp in current time interval
                inds_interp = np.logical_and(np.array(x_interp) >= t[0], np.array(x_interp) <= t[-1])
                # Evaluate interpolation for values of x_interp in current time interval
                y_interp[inds_interp] = func(x_interp_unix[inds_interp])
                
                # Update used indices if x_vals
                valid_inds = np.logical_or(valid_inds, inds)
                # Update used indices if x_interp
                valid_inds_interp = np.logical_or(valid_inds_interp, inds_interp)
            
            except ValueError as e:
                # If too few values lie in current time interval, ValueError is raised.
                # In this case, just skip current time interval and interpolate linearly later.
                print(f"Skipping interval from {t[0]} to {t[-1]}")
        
        # Apply linear interpolation to all values of x_interp
        func = interp1d(x_unix, y_vals, kind=1)
        # Evaluate linear inteprolation for all indices of x_interp which haven't been used yet
        y_interp[np.logical_not(valid_inds_interp)] = func(x_interp_unix[np.logical_not(valid_inds_interp)])
        
        # Cast result back to list
        y_interp = list(y_interp)
        
    else:
        # Splitting interpolation regions is only implemented for datetime yet.
        assert max_interval is None, "max_interval not yet implemented for x-axes of types other than datetime"
    
        # Create x-values for evaluation of interpolation spline
        x_interp = np.arange(x_vals[0], x_vals[-1], delta)     
        
        # If old values should be kept, add old values, remove duplicates via set and sort
        if keep_old:
            x_interp = sorted(list(set(x_interp + x_vals)))
        
        # Interpolate according to chosen method
        if interpolation_mode == "bspline":
            func = BSpline(x_vals, y_vals, k = order)
        elif interpolation_mode == "interp1d":
            func = interp1d(x_vals, y_vals, kind=order)
        elif interpolation_mode == "univ":
            func = UnivariateSpline(x_vals, y_vals, k=order)     
        
        # Apply interpolation to all values of x_interp
        y_interp = func(x_interp)

    # Determine all indices which stem from interpolation. Using set
    # makes searching faster, as searching in set is O(1) vs O(N) in lists
    x_set = set(x_vals)
    inds_interp = [i for i, x in enumerate(x_interp) if x not in x_set]

    return list(x_interp), list(y_interp), inds_interp

def padData(data: Dict, pad_to_len_of: str = "datetime", pad_len_of: str = "source_id"):
    """
    Pad list of property 'pad_len_of' to match the length of property 'pad_to_len_of'.
    
    Arguments:
        data: Dictionary containing data
        pad_to_len_of: Name of property whose size should be padded to
        pad_to_len: Name of property whose size should be padded
    
    Returns:
        VOID: works inplace 
    """
    assert len(set(data[pad_len_of])) == 1, "Property which is supposed to be padded should only have one value"
    val = list(set(data[pad_len_of]))[0]
    data[pad_len_of] = [val for i in range(len(data[pad_to_len_of]))]
    

def flattenDict(data_split: Dict, property_name: str = "property_name", sort_by: str = "datetime"):
    """
    Flatten a dictionary along column of 'property_name' and sort the columns by (sort_by, property_name).
    
    Arguments:
        data_split: Dictionary containing data, split according to values of 'property_name'
        property_name: Name of column where values used for splitting are saved. Used as secondary key.
        sort_by: Property to sort by (secondary key is given by 'property_name')
    
    Returns:
        data: Flattened dictionary 
    """
    data = defaultdict(list)
    for k in data_split.keys():
        for l, vals in data_split[k].items():
            data[l] += vals
    
    tmp = zip(data[sort_by], data[property_name])
    order = np.arange(0, len(data[sort_by]), dtype=int)
    order = [o for t, o in sorted(zip(tmp, order))]
    
    for k in data.keys():
        data[k] = [data[k][o] for o in order]
        
    return data
    

def writeCSV(filename: str, data: Dict, log_structure = ["source_id","datetime","property_name","temperature"]):
    """
    Write data to CSV-file.
    
    Arguments:
        filename: Filename to save data to
        data: Data that is supposed to be saved
        log_structure: structure for logging quantities
    
    Returns:
        VOID 
    """
    with open(filename, "w") as f:
        f.write(",".join(log_structure) + "\n")
        for i in range(len(data[log_structure[0]])):
            f.write(",".join([str(data[log][i]) for log in log_structure]) + "\n")
            
