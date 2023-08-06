Changelog
=========

Not Yet Released
----------------

- A new infrastructure for converting ``EventList`` and ``LightCurve`` objects into Astropy ``TimeSeries``
- A new infrastructure for converting most ``Stingray`` classes into Astropy ``Table`` objects
- Save and load of most ``Stingray`` classes to/from many different file formats (``pickle``, ``ECSV``, ``HDF5``, ``FITS``, and all formats compatible with Astropy Table)
- Accept input ``EventList`` in ``DynamicalPowerSpectrum``
- Implement Gardner-Done normalization (1 for perfect correlation, -1 for perfect anticorrelation) for ``Auto/Crosscorrelation``
- Make modulation upper limit in ``(Averaged)Powerspectrum`` work with any normalization
- Dropped support to Python <3.8
- Multi-taper periodogram, including a Lomb-Scargle implementation for non-uniformly sampled data.
- Upper limits on pulsations in periodograms and Z searches
- New stingray.fourier module containing the basic timing products, usable on ``numpy`` arrays
- Lots of performance improvements in the ``AveragedCrossspectrum`` and ``AveragedPowerspectrum`` classes
- New methods in ``Crossspectrum`` and ``Powerspectrum`` to load data from specific inputs: ``from_events``, ``from_lightcurve``, ``from_time_array``, ``from_lc_list``
    - ``from_time_array`` was also tested using memory-mapped event lists as inputs: useful in very large datasets
- New and improved spectral timing methods: ``ComplexCovarianceSpectrum``, ``CovarianceSpectrum``, ``LagSpectrum``, ``RmsSpectrum``
- Improved error bars on cross-spectral and spectral timing methods
- Some deprecated features are now removed
- ``PSDLogLikelihood`` now also works with a log-rebinned PDS
- PDS/CrossSp initially store the unnormalized power, and convert it on the fly when requested, to any normalization
- Lots of bug fixes

`Full list of changes`__

__ https://github.com/StingraySoftware/stingray/compare/v0.3...main

v0.3 (2021-05-31)
-----------------

- Lots of performance improvements
- Faster simulations
- Averaged Power spectra and Cross spectra now handle Gaussian light curves correctly
- Fixes in rebin functions
- New statistical functions for signal detection in power spectra and pulsar search periodograms
- Much improved FTOOL-compatible mission support
- New implementation of the FFTFIT method to calculate pulsar times of arrival
- H-test for pulsar searches
- Z^2_n search adapted to binned and normally distribute pulse profiles
- Large data processing (e.g. from NICER) allowed
- Rebinning function now accepts unevenly sampled data
- New saving and loading from/to Astropy Tables and Timeseries
- Improved I/O to ascii, hdf5 and other formats
- Rehaul of documentation

`Full list of changes`__

__ https://github.com/StingraySoftware/stingray/compare/v0.2...v0.3

v0.2 (2020-06-17)
-----------------

- Added Citation info
- Fixed various normalization bugs in Powerspectrum
- Speedup of lightcurve creation and handling
- Made code compatible with Python 3.6, and dropped support to Python 2.7
- Test speedups
- Dead time models and Fourier Amplitude Difference correction
- Roundtrip of LightCurve to lightkurve objects
- Fourier-domain accelerated search for pulsars
- Adapt package to APE-17
- Periodograms now also accept event lists (instead of just light curves)
- Allow transparent MJDREF change in event lists and light curves

`Full list of changes`__

__ https://github.com/StingraySoftware/stingray/compare/v0.1.3...v0.2

v0.1.3 (2019-06-11)
-------------------

- Bug fixes

v0.1.2
------

- Bug fixes

v0.1.1
------

- Bug fixes

v0.1 (2019-05-29)
-----------------

- Initial release.
