import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel
from scipy.interpolate import lagrange
from scipy.signal import find_peaks
import tmg_constants

"""
A collection of functions used to analyze TMG time series signals.
Functionality includes:
    - Compute the standard Dm, Td, Tc, Ts, Tr parameters of a TMG signal
    - Compute the time derivative of a TMG signal
    - Compute parameters describing the derivative of the TMG signal, e.g.
      rdd_max, rdd_min, rdd_max_time, rdd_min_time, etc...
"""

def get_params_of_tmg_signal(tmg, dt=tmg_constants.TMG_DT, 
        log_params=False, log_aux_params=False, show_plot=False):
    """
    Computes the TMG and RDD parameters of a single TMG time-series signal.
    The following parameters are computed: 
    Dm, Td, Tc, Ts, Tr, rdd_max, rdd_max_time, rdd_min, rdd_min_time, 
    rdd_peak_to_peak, rdd_max_min_time

    Parameters
    ----------
    tmg : ndarray
        1D Numpy array holding a TMG signal, i.e. a sequence of muscle
        displacement points measured with respect to time.
    dt : double
        Time in [ms] between subsequent points in the TMG signal
        The function assumes uniform spacing in time between data points.
    show_plot : bool
        Set to True to show a plot of the TMG signal.
    log_params : bool
        Set to True to print values of computed parameters to console.
    log_aux_params : bool
        Set to True to print values of auxiliary parameters to console,
        i.e. parameters used in the process of computing the standard
        TMG parameters but not returned as a final result.
    
    Returns
    -------
    params : ndarray
        1D, 14-element Numpy array holding the TMG signal's 
        parameters in the following order:
            [dm, td, tc, ts, tr, p1, p2, p3,
            rdd_max, rdd_min, rdd_peak_to_peak,
            rdd_max_time, rdd_min_time, rdd_max_min_time]

    """
    # Time values on which the TMG signal is defined
    t = np.arange(0, len(tmg))  

    max_indices = get_tmg_maxima(tmg)
    max_index = max_indices[0]
    dm = tmg[max_index]

    # Example: t10_left is the time from the start of the TMG signal
    # to the point at which the TMG signal reaches 10 percent
    # of its maximum value on the left of the TMG signal maximum,
    # i.e. when the TMG signal is increasing.
    t10_left = interpolate_time_of_target_amplitude(t, tmg, 0.1*dm, max_indices,
            find_time_left_of_peak=True)
    t50_left = interpolate_time_of_target_amplitude(t, tmg, 0.5*dm, max_indices,
            find_time_left_of_peak=True)
    t90_left = interpolate_time_of_target_amplitude(t, tmg, 0.9*dm, max_indices,
            find_time_left_of_peak=True)
    t90_right = interpolate_time_of_target_amplitude(t, tmg, 0.9*dm, max_indices,
            find_time_left_of_peak=False)
    t50_right = interpolate_time_of_target_amplitude(t, tmg, 0.5*dm, max_indices,
            find_time_left_of_peak=False)

    # # --------------------------------------------- #
    if log_aux_params:
        print("t10_left: \t({:.3f}, {:.3f})".format(t10_left, 0.1*dm))
        print("t50_left: \t({:.3f}, {:.3f})".format(t50_left, 0.5*dm))
        print("t90_left: \t({:.3f}, {:.3f})".format(t90_left, 0.9*dm))
        print("t90_right:\t({:.3f}, {:.3f})".format(t90_right, 0.9*dm))
        print("t50_right:\t({:.3f}, {:.3f})".format(t50_right, 0.5*dm))
    if show_plot:
        plt.plot(t, tmg, marker='o')
        plt.show()
    # # --------------------------------------------- #

    # Compute standard TMG time parameters
    # --------------------------------------------- #
    td = t10_left
    tc = t90_left - t10_left
    ts = t50_right - t50_left
    tr = t50_right - t90_right
    p1 = tc + td
    p2 = (tc + td)/tr
    p3 = (0.9 * dm)/(tc + td)
    # --------------------------------------------- #

    # Compute derivative of TMG signal (rdd in TMG lingo)
    # --------------------------------------------- #
    rdd = np.gradient(tmg, tmg_constants.TMG_DT)  # time derivative of the TMG signal
    rdd_max_time_estimate = np.argmax(rdd)
    rdd_max_time, rdd_max = interpolate_extrema(t, rdd, rdd_max_time_estimate, find_max=True)
    rdd_min_time_guess = np.argmin(rdd)
    rdd_min_time, rdd_min = interpolate_extrema(t, rdd, rdd_min_time_guess, find_max=False)
    rdd_peak_to_peak = rdd_max - rdd_min
    rdd_max_min_time = rdd_min_time - rdd_max_time
    # --------------------------------------------- #

    return np.array([dm, td, tc, ts, tr, p1, p2, p3, rdd_max, rdd_min,
        rdd_peak_to_peak, rdd_max_time, rdd_min_time, rdd_max_min_time])


def get_tmg_maxima(tmg):
    """
    Returns the indices of local maxima in the TMG signal.
    The first maximum is used in practice to find the TMG parameter Dm; 
    the later maxima, if present, are useful when computing Tr and Ts.

    The function only returns maxima that occur after the parameter
    constants.REJECT_TMG_PEAK_INDEX_LESS_THAN. Reason: the filtering built in to
    the TMG acquisition system introduces occasional non-physical local maxima in 
    the first few data points at the start of the signal as an artifact from
    filtering the raw measured signal with an IIR lowpass filter---I do not know
    the exact filter specs, perhaps a 5-th order Butterworth at ~15 Hz cutoff?

    Parameters
    ----------
    tmg : ndarray
        1D Numpy array holding the displacement points of a TMG signal
    
    Returns
    -------
    max_indices : ndarray
        Indices of all maxima in `tmg` that occur.
        after `REJECT_TMG_PEAK_INDEX_LESS_THAN`.
        The first element corresponds to Dm
    
    """
    max_indices = find_peaks(tmg)[0]

    # Keep only maxima after REJECT_TMG_PEAK_INDEX_LESS_THAN
    return max_indices[(max_indices > tmg_constants.REJECT_TMG_PEAK_INDEX_LESS_THAN)]


def interpolate_time_of_target_amplitude(t, tmg, target_amp, max_indices,
        find_time_left_of_peak, window_size=tmg_constants.TIME_INTERP_WINDOW_SIZE):
    """
    Estimates the time at which a TMG signal reaches the target amplitude in x_target

    Parameters
    ----------
    t : ndarray
        1D Numpy array holding time points in [ms] 
        on which the TMG signal is defined
    tmg : ndarray
        1D Numpy array holding TMG signal in [mm]
    target_amp : double
        Target amplitude of the TMG signal
    max_indices : ndarray
        Indices of all physical maxima in `tmg`; see `get_tmg_extrema`
    find_time_left_of_peak : bool
        True to find the time at which the TMG signal reaches `x_target`
        on the left of the TMG peak (while TMG signal is increasing).
        False to find the time at which the TMG signal reaches `x_target`
        on the right of the TMG peak (while TMG signal is decreasing).
    window_size : int
        The number of points to use on either side of the closest point 
        in TMG signal to target amplitude for interpolating polynomial.
        Polynomial passes through (2*window_size + 1) points total
    
    """
    dm_index = max_indices[0]
    # First find the index of the displacement data point in `tmg`
    # that is closest to `target_amp`
    if find_time_left_of_peak:
        # Search TMG signal from start to Dm
        target_index_estimate = np.argmin(np.abs(tmg[:dm_index] - target_amp))
    else:
        # The unlikely event that there is only one local maximum 
        # in the entire TMG signal.
        if len(max_indices) == 1:
            target_index_estimate = np.argmin(np.abs(tmg[dm_index:] 
                - target_amp)) + dm_index

        # If there are multiple local maxima in the TMG signal
        else:
            # Initial value, which will almost certainly be reset in the `for`
            # loop below, but serves as a fallback case.
            target_index_estimate = np.argmin(np.abs(tmg[dm_index:] 
                - target_amp)) + dm_index

            # Loop through TMG signal from Dm peak forward and find first time
            # when the TMG signal crosses target_amp
            x_prev = tmg[dm_index]
            for (i, x) in enumerate(tmg[dm_index + 1:]):
                # Test if target_amp occured between x_prev and x
                # while TMG signal is decreasing
                if x < target_amp and x_prev > target_amp:
                    # Note addition of dm_index offset since loop begins at Dm
                     target_index_estimate = i + dm_index  
                     break

    # TMG data point in the TMG signal closest to target amplitude
    target_amp_estimate = tmg[target_index_estimate]

    if target_amp_estimate < target_amp:  # if best guess for target amplitude is less than target
        if find_time_left_of_peak:
            t_window = t[target_index_estimate - window_size + 1: target_index_estimate + window_size + 1]
            x_window = tmg[target_index_estimate - window_size + 1: target_index_estimate + window_size + 1]
        else:
            t_window = t[target_index_estimate - window_size: target_index_estimate + window_size]
            x_window = tmg[target_index_estimate - window_size: target_index_estimate + window_size]

    elif target_amp_estimate > target_amp:  # if best guess for target amplitude is larger than target
        if find_time_left_of_peak:
            t_window = t[target_index_estimate - window_size: target_index_estimate + window_size]
            x_window = tmg[target_index_estimate - window_size: target_index_estimate + window_size]
        else:
            t_window = t[target_index_estimate - window_size + 1: target_index_estimate + window_size + 1]
            x_window = tmg[target_index_estimate - window_size + 1: target_index_estimate + window_size + 1]

    # The extremely unlikely case that the target displacement is actually in the 
    # sampled data up to all decimal points in the scope of double precision.
    else:  
        return t[target_index_estimate]

    poly = lagrange(t_window, x_window)
    coef = poly.coef

    # Subtract off x_target to prepare polynomial for use with a root-finding algorithm
    coef[-1] -= target_amp  

    roots = np.roots(coef)  # find interpolation polynomial's roots

    # The polynmial will in general have multiple roots.
    # Return the closest to the time of the target amplitude.
    # Also case to real to remove residual imaginary part left
    # by the root-finding algorithm.
    return np.real(roots[np.argmin(np.abs(roots - t[target_index_estimate]))])


def interpolate_extrema(t, x, extrema_index, find_max=True, 
        poly_dt=tmg_constants.EXTREMA_INTERP_DT, 
        window_size=tmg_constants.EXTREMA_INTERP_WINDOW_SIZE):
    """
    Used to estimate the values and times of TMG and RDD signal extrema with
    finer granularity than the TMG signal's 1kHz sampling explicitly allows.
    Interpolates a Lagrange polynomial around the extrema point, evaluates 
    the polynomial on a finely-spaced time grid (e.g. an order of magnitude
    finer than the TMG signal's 1ms spacing), and finds the time and value
    of the polynomial on the grid. 

    Notes:
    - The interpolating polynomial's extrema are not found analytically,
      even though this is in principle possible. The extra precision is
      irrelevant and probably non-physical since the interpolation is
      an estimate anyway.
    - The entire TMG/RDD signal is passed in. This makes code a bit cleaner
      on the calling end, even if in principle one needs to pass in only a
      small window of time and displacement points centered around the extrema.

    Parameters
    ----------
    t : ndarray
        1D Numpy array holding time points in [ms] on which the TMG signal is defined
    x : ndarray
        1D Numpy array holding TMG or RDD signal in [mm] or [mm/s]
    extrema_index : int
        Index at which the inputted signal `x` reaches its minimum or maximum value.
    find_max : bool
        True to find value and time of a maximum; False to find value/time of a minimum.
    poly_dt : double
        Time granularity in [ms] for the time grid on which to evaluate 
        the interpolating polynomial.
        (E.g. an order of magnitude or two smaller than TMG signals 1ms granularity.)
    window_size : int
        The number of points to use on either side of the closest point 
        in TMG/RDD signal to target amplitude for interpolating polynomial.
        Polynomial passes through (2*window_size + 1) points total.
    
    """
    t_window = t[extrema_index - window_size: extrema_index + window_size + 1]
    x_window = x[extrema_index - window_size: extrema_index + window_size + 1]

    poly = lagrange(t_window, x_window)

    # Discrete time values and points on which to evaluate
    # the interpolating polynomia.
    num_poly_points = int((t_window[-1] - t_window[0]) / poly_dt)
    t_poly = np.linspace(t_window[0], t_window[-1], num_poly_points)
    x_poly = poly(t_poly)

    if find_max:
        extrema_index = np.argmax(x_poly)
    else:
        extrema_index = np.argmin(x_poly)

    x_extrema = x_poly[extrema_index]
    extrema_time = t_poly[extrema_index]
    return extrema_time, x_extrema

