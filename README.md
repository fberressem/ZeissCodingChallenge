# ZeissCodingChallenge
Repository to work on Zeiss' coding challenge for position as data scientist. The goal here is to interpolate temperature data.

## Quickstart
Run `bash run.setup.sh` to set up virtual environment and install requirements via pip. Then run `bash run.sh -K` to reproduce results.

## Installation
Set up a virtual environment and install all requirements by running
```console
mkdir -p Venv
source Venv/bin/activate
pip install numpy scipy matplotlib
```
The versions used here, were:
numpy==1.22.3, scipy==1.8.0 and matplotlib==3.5.1

## Run tests
To run the provided tests, activate the virtual environment via

```console
source Venv/bin/activate
```
and run 

```console
python3 test.py
```

## Run interpolation
To run the interpolation, either use the provided bash script `run.sh` or use the python script `main.py` after activating the virtual environemnt via
```console
source Venv/bin/activate
```

In both cases the following arguments can be passed to the scripts:
| Argument      | Description |
| ----------- | ----------- |
| `-F`, `--filename` | Filename to read data from (default: *sample_temperature_data_for_coding_challenge.csv*)|
| `-O`, `--output` | Output to save interpolated data to (default: *temperature.csv*)|
| `-S`, `--spline_order` | Order of spline for interpolation (default: *1*) |
| `-T`, `--timedelta` | Timedelta for interpolation in minutes (default: *60*)|
| `-M`, `--max_interval` | Maximum time-interval in minutes. Time intervals larger than this value are interpolated linearly. (default: *None*)|
| `-P`, `--plot` | Plot temperatures if enabled (default: *False*)|
| `-K`, `--keep_old` | Keep old data during interpolation if enabled (default: *False*)|
| `-I`, `--interpolation_mode` | Method to use for interpolation (default: *interp1d*)|

To reproduce the provided results, run `bash run.sh -K`.
The best results can be obtained by using *interp1d* as interpolation mode and a spline of order <= 2 (with spline order = 1 corresponding to a linear interpolation and spline order = 0 corresponding to simply reproducing the values) together with a max_interval of more than a day (*i.e.* more than 1440 minutes) so as to split the interpolation into interpolations of distinct regions. By using `-K` you can keep the old data in addition to the interpolated values. Splitting the interpolation regions is useful, as the large time intervals between different measurements strongly restrict the functional form of the spline and actually dominate it, leading to huge values in between measurements and rather bad interpolation (at least visually) in each measurement.
