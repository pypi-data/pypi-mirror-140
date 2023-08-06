import pandas as pd
import os
import tmg, tmg_constants

"""
The script `tmg.py` offers the function `get_params_of_tmg_signal`, which 
computes and returns the TMG parameters of a single TMG signal stored 
as a 1-dimensional Numpy array.
While accepting a Numpy array in `get_params_of_tmg_signal` turns out to lead to
more modular code, it is up to the user to extract TMG signals from the 
Excel file format used by the TMG measurement system and convert these signals
to admittedly more Pythonic Numpy arrays.

This script provides some boilerplate I/O and file conversion code to make it
easier to extract TMG signals from TMG-formatted Excel measurement files and
to compute parameters from these signals.
"""

def get_tmg_params_of_single_measurement(measurement_num=0, xlsx_file = "../sample-data/EM.xlsx"):
    """
    Computes the TMG parameters of a single TMG measurement/signal/time-series
    in a standard TMG-formatted Excel file, which will generally contain 
    multiple measurements.

    Parameters
    ----------
    measurement_num : int
        Zero-based measurement number for which to calculate parameters.
    
    """
    # Read measurements from Excel file into a Pandas DataFrame
    df = xlsx_to_pandas_df(xlsx_file)

    # Extract 1D TMG signal as Pandas Series
    tmg_signal = df.iloc[:, measurement_num]

    # Compute TMG parameters
    params = tmg.get_params_of_tmg_signal(tmg_signal.to_numpy())

    # Print params in human-readable format
    param_names = tmg_constants.TMG_PARAM_NAMES
    for i, param in enumerate(params):
        print("{} {:.2f}".format(param_names[i], param))


def get_tmg_params_of_file(xlsx_input_file = "../../sample-data/EM.xlsx",
        output_file = "../../sample-output/EM-params.csv"):
    """
    Computes the TMG parameters of all measurements 
    in a standard TMG-formatted Excel file.
    Writes parameters in human-readable CSV format to `output_file`.

    """
    # Read measurements from Excel file into a Pandas DataFramee
    df = xlsx_to_pandas_df(xlsx_input_file)

    measurement_names = []
    param_names = tmg_constants.TMG_PARAM_NAMES

    # First add parameters to a list, then create a DataFrame from the list
    param_list = []

    # Loop through each measurement number and TMG signal in Excel file
    for (m, tmg_signal) in df.iteritems():
        params = tmg.get_params_of_tmg_signal(tmg_signal.to_numpy())
        param_list.append(params)
        measurement_names.append("Measurement {}".format(m))

    param_df = pd.DataFrame(param_list).transpose()
    param_df.columns=measurement_names
    param_df.index=param_names
    param_df.to_csv(output_file)


def get_tmg_params_of_directory(input_dir="../../sample-data/",
        output_dir="../../sample-output/"):
    """
    Computes the TMG parameters for all measurements in each 
    of the TMG-formatted Excel files in a directory.
    Assumes all `*.xlsx` files in the inputted directory
    are TMG-formatted Excel files.
    For each file, writes parameters in human-readable CSV format
    to a separate CSV file in `output_dir`.

    """
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".xlsx" ):  
            output_filename = filename.replace(".xlsx", "-params.csv")
            get_tmg_params_of_file(xlsx_input_file=input_dir + filename,
                    output_file=output_dir + output_filename)


def xlsx_to_pandas_df(xlsx_file, max_signal_rows=tmg_constants.TMG_MAX_ROWS):
    """
    Utility function for reading the measurements in a TMG-formatted Excel file
    into a Pandas dataframe.
    Drops the following information from the Excel file:
    - The first column  (which does not contain TMG signal data)
    - The first constants.DATA_START_ROW rows (contain metadata but no signal)

    Parameters
    ----------
    xlsx_file : str
        Full path to a TMG-formatted Excel measurement file
    max_signal_rows : int
        Number of rows (i.e. data points, i.e. milliseconds assuming
        1 kHz sampling) of inputted TMG signal to analyze, since most
        relevant information occurs in the first few hundred milliseconds only.

    Returns
    -------
    df : DataFrame
        Pandas dataframe equivalent of Excel file's measurement
    
    """
    return pd.read_excel(xlsx_file, engine='openpyxl', header=None,
            skiprows=tmg_constants.TMG_DATA_START_ROW,
            nrows=max_signal_rows).drop(columns=[0])

    
if __name__ == "__main__":
    get_tmg_params_of_single_measurement()
    get_tmg_params_of_file()
    get_tmg_params_of_directory()
