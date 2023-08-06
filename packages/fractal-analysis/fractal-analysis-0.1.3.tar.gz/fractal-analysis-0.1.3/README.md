# Fractal Analysis
Fractal and multifractal methods, including

- fractional Brownian motion (FBM) tester
- multifractional Brownian motion (MBM) tester

## To install
To get started, simply do:
```
pip install fractal-analysis
```
or check out the code from out GitHub repository.

You can now use the package in Python with:
```
from fractal_analysis import tester
```

## Examples
Import:
```
from fractal_analysis.tester.series_tester import MBMSeriesTester, FBMSeriesTester
from fractal_analysis.tester.critical_surface import CriticalSurfaceFBM, CriticalSurfaceMFBM
```
To test if a series ```series``` is FBM, one needs to use ```CriticalSurfaceFBM``` with length of the series ```N```
and the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```) 
```
fbm_tester = FBMSeriesTester(critical_surface=CriticalSurfaceFBM(N=N, alpha=0.05))
```

To test if the series is FBM with holder exponent 0.3 and use auto estimated sigma square (set ```sig2=None```):

```
is_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=None)
```
If the output contains, for example:
> Bad auto sigma square calculated with error 6.239236333681868. Suggest to give sigma square and rerun.

The auto sigma square estimated is not accurate. One may want to manually choose a sigma square and rerun. For example:
```
is_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=1)
```
To test if the series is MBM, one needs to use ```CriticalSurfaceMFBM``` with length of the series ```N```
and the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```) 
```
mbm_tester = MBMSeriesTester(critical_surface=CriticalSurfaceMFBM(N=N, alpha=0.05))
```
To test if the series is MBM with a given holder exponent series ```h_mbm_series``` and use auto estimated sigma square:
```
is_mbm, sig2 = mbm_tester.test(h=h_mbm_series, x=series, sig2=None)
```
Be aware that ```MBMSeriesTester``` requires ```len(h_mbm_series)==len(series)```.

## Use of cache
Use caching to speed up the testing process. If the series ```x``` for testing is unchanged and multiple ```h``` 
and/or ```sig2``` are used, one may want to set 
```is_cache_stat=True``` to allow cache variable ```stat```. If ```h``` and ```sig2``` are unchanged and multiple ```x```
are used, one may want to set ```is_cache_quantile=True``` to allow cache variable ```quantile```. For example:
```
mbm_tester = MBMSeriesTester(critical_surface=CriticalSurfaceMFBM(N=N, alpha=0.05), is_cache_stat=True, is_cache_quantile=False)
```

