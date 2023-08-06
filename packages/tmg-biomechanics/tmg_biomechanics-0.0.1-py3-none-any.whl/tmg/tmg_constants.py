# The first row (assuming zero-based row indexing) containing 
# TMG signal data in a standard TMG format Excel file.
TMG_DATA_START_ROW = 24

# Time in milliseconds between successive points in a TMG signal (which is sampled at 1kHz)
TMG_DT = 1

# Maximum number of rows (datapoints) of the TMG signal to analyze.
# Also the number of milliseconds to analyze, assuming 1kHz sampling.
TMG_MAX_ROWS = 500  

# The number of points to use for interpolating polynomial when estimating 
# the times of the TMG parameters td, tc, ts and tr
TIME_INTERP_WINDOW_SIZE = 2  

# [ms] time granularity to use when interpolating td, tc, ts and tr times
TIME_INTERP_DT = 0.01  

# Occasionally TMG signal will have artificial, filter-induced local maxima in
# the first few data points that can be confusing when finding Dm. This 
# parameter is used to reject any local maxima that occur before 
REJECT_TMG_PEAK_INDEX_LESS_THAN = 8

# Number of points to use on either side of extrema when interpolating
EXTREMA_INTERP_WINDOW_SIZE = 2  

# [ms] time granularity to use when interpolating extrema (generally of rdd signal)
EXTREMA_INTERP_DT = 0.01  

# Names of TMG parameters
TMG_PARAM_NAMES = ["Dm:", "Td:", "Tc:", "Ts:", "Tr:", "P1:", "P2:", "P3:",
        "RDD Max:", "RDD Min:", "RDD Peak to Peak:",
        "RDD Max Time:", "RDD Min Time:", "Max to Min Time:"]

