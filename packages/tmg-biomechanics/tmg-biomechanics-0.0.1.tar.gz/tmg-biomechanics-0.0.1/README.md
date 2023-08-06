# TMG
Utilities for time-series analysis of tensiomyography (TMG) measurement data.
TMG is used to non-invasively measure muscle belly displacement with respect to time during electrically induced isometric contraction, and is used in both sports diagnostics and medical contexts.
To quickly visualize a TMG measurement, [see this ~90 second animation](https://www.youtube.com/watch?v=RwsBNEcN6PA).
For more information about TMG measurements, see [the TMG website's description of the TMG measurement device](https://www.tmg-bodyevolution.com/sports/tmg-measuring-device/).

The Python script `src/tmg/tmg.py` does the following:
- Compute the standard TMG signal parameters `Dm`, `Td`, `Tc`, `Ts`, `Tr`.
- Compute the time derivative of a TMG signal.
- Compute parameters describing the derivative of the TMG signal:
  `rdd_max`, `rdd_min`, `rdd_peak_to_peak`, `rdd_max_time`, and `rdd_min_time`.
