"""P20 exact classical bounds. NEVER promote published SPD to independently
certified same-vehicle arithmetic speed without external instrument evidence."""
import math
def required_source_lag(delay_minutes):
    if not isinstance(delay_minutes,int) or delay_minutes<0:
        raise ValueError("nonnegative integer minute delay required")
    return 1+(delay_minutes+9)//10
def conditional_vehicle_time_bounds(n,L,m,a,b):
    """N fixed-length L-km constant-speed vehicles, known arithmetic speed mean m,
    every actual speed within [a,b]. Returns SHARP min/max vehicle-hours."""
    if not isinstance(n,int) or n<1 or not (L>0 and a>0 and a<=m<=b):
        raise ValueError("invalid conditional instrument certificate")
    low=n*L/m
    if a==b:return (low,low)
    k=min(n,math.floor(n*(m-a)/(b-a)+1e-10))
    rem=max(0,n*(m-a)-k*(b-a))
    high=L*(k/b+(n-k)/a) if rem<1e-10 else L*(k/b+1/(a+rem)+(n-k-1)/a)
    return low,high
def admit_independent_detector(r):
    needs=("instrument","site","direction","lane_set","vehicle_coverage",
           "clock_alignment","bounded_calibration_error","independent_acquisition",
           "separate_processing_evidence")
    return all(r.get(f) not in (None,"",False) for f in needs)
