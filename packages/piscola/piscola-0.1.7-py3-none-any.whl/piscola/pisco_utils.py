import numpy as np

def flux2mag(flux, zp, flux_err=0.0):
    """Converts fluxes to magnitudes, propagating errors if given.

    Note: if there are negative or zero fluxes, these are converted to NaN values.

    Parameters
    ----------
    flux : array
        Array of fluxes.
    zp : float or array
        Zero points.
    flux_err : array, default ``0.0``
        Array of flux errors.

    Returns
    -------
    mag : array
        Fluxes converted to magnitudes.
    mag_err : array
        Flux errors converted to errors in magnitudes.
    """

    if type(flux)==np.ndarray:
        flux_ = np.array([f if f>=0.0 else np.nan for f in flux ])  # turns negative and 0.0 values to NaN
    elif flux<=0.0:
        flux_ = np.nan
    else:
        flux_ = flux
        
    mag = -2.5*np.log10(flux_) + zp
    mag_err = np.abs( 2.5*flux_err/(flux_*np.log(10)) )

    return mag, mag_err

def mag2flux(mag, zp, mag_err=0.0):
    """Converts magnitudes to fluxes, propagating errors if given.

    Parameters
    ----------
    mag : array
        Array of magnitudes.
    zp : float or array
        Zero points.
    mag_err : array, default ``0.0``
        Array of magnitude errors.

    Returns
    -------
    flux : array
        Magnitudes converted to fluxes.
    flux_err : array
        Magnitude errors converted to errors in fluxes.
    """

    flux = 10**( -0.4*(mag-zp) )
    flux_err =  np.abs( flux*0.4*np.log(10)*mag_err )

    return flux, flux_err

def change_zp(flux, zp, new_zp):
    """Converts flux units given a new zero-point.

    **Note:** this assumes that the new zero-point is in the same magnitude system as the current one.

    Parameters
    ----------
    flux : float or array
        Fluxes.
    zp : float or array
        Current zero-point for the given fluxes.
    new_zp : float or array
        New zero-point to convert the flux units.

    Returns
    -------
    new_flux : float or array
        Fluxes with with a new zero-point.

    """

    new_flux = flux*10**( -0.4*(zp - new_zp) )

    return new_flux

def trim_filters(response):
    """Trim the leading and trailing zeros from a 1-D array or sequence, leaving
    one zero on each side. This is a modified version of numpy.trim_zeros.

    Parameters
    ----------
    response : 1-D array or sequence
        Input array.

    Returns
    -------
    first : int
        Index of the last leading zero.
    last : int
        Index of the first trailing zero.
    """

    first = 0
    for i in response:
        if i != 0.:
            if first == 0:
                first += 1  # to avoid filters with non-zero edges
            break
        else:
            first = first + 1

    last = len(response)
    for i in response[::-1]:
        if i != 0.:
            if last == len(response):
                last -= 1  # to avoid filters with non-zero edges
            break
        else:
            last = last - 1

    first -= 1
    last += 1

    return first, last


def extrapolate_mangling_edges(x, y, yerr, x_edges, extra_extension=0.0):
    """"Extrapolates the edges of y according to the giving edges in x, x_edges.

    Parameters
    ----------
    x_data : array
        Independent values.
    y_data : array
        Dependent values.
    yerr_data : array, int
        Dependent value errors.
    x_edges: array-like
        Minimum and maximum x-axis values. These are used to extrapolate both edges.
    extra_extension: float, default ``0.0``
        This value is added to extend the edges even more. It might look redundant, but it has its purpose.

    Returns
    -------
    x : array
        Extrapolated independent values.
    y : array
        Extrapolated dependent values.
    yerr : array, int
        Extrapolated dependent value errors.
    """

    x_min, x_max = x_edges
    x_min -= extra_extension
    x_max += extra_extension

    # linear extrapolation
    pmin = np.polyfit(x[:2], y[:2], deg=1)
    pmax = np.polyfit(x[-2:], y[-2:], deg=1)
    y_left, y_right = np.poly1d(pmin)(x_min), np.poly1d(pmax)(x_max)

    # avoid negative values
    if y_left<0:
        y_left=0
    if y_right<0:
        y_right=0
    y = np.r_[y_left, y, y_right]
    x = np.r_[x_min, x, x_max]
    try:
        yerr_min = np.sqrt(yerr[0]**2 + yerr[1]**2)
        yerr_max = np.sqrt(yerr[-1]**2 + yerr[-2]**2)
        yerr = np.r_[yerr_min, yerr, yerr_max]
    except:
        pass

    return x, y, yerr
