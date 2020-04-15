"""
Gravity corrections like Bouguer corrections, free air, spherical cap and 
atmospheric.

Refer to Hinze(2005) for formula.
http://library.seg.org/doi/10.1190/1.1988183

"""
import numpy as np

from .constants import GRAVITATIONAL_CONST


def bouguer_correction(topography, density_crust=2670, density_water=1040):
    """
    Gravitational effect of topography using a Bouguer plate approximation

    Used to remove the gravitational attraction of topography above the
    ellipsoid from the gravity disturbance. The infinite plate approximation is
    adequate for regions with flat topography and observation points close to
    the surface of the Earth.

    This function calculates the classic Bouguer correction:

    .. math::

        g_{bg} = 2 \pi G \rho h

    in which :math:`G` is the gravitational constant and :math:`g_{bg}` is the
    gravitational effect of an infinite plate of thickness :math:`h` and
    density :math:`\rho`.

    In the oceans, subtracting normal gravity from the observed gravity results
    in over correction because the normal Earth has crust where there was water
    in the real Earth. The Bouguer correction for the oceans aims to remove
    this residual effect due to the over correction:

    .. math::

        g_{bg} = 2 \pi G (\rho_w - \rho_c) |h|

    in which :math:`\rho_w` is the density of water and :math:`\rho_c` is the
    density of the crust of the normal Earth. We need to take the absolute
    value of the bathymetry :math:`h` because it is negative and the equation
    requires a thickness value (positive).

    Parameters
    ----------
    topography : array or :class:`xarray.DataArray`
        Topography height and bathymetry depth in meters.
        Should be referenced to the ellipsoid (ie, geometric heights).
    density_crust : float
        Density of the crust in :math:`kg/m^3`.
        Used as the density of topography on land and the density of the normal
        Earth's crust in the oceans.
    density_water : float
        Density of water in :math:`kg/m^3`.

    Returns
    -------
    grav_bouguer : array or :class:`xarray.DataArray`
        The gravitational effect of topography and residual bathymetry in mGal.

    """
    # Need to cast to array to make sure numpy indexing works as expected for
    # 1D DataArray topography
    oceans = np.array(topography < 0)
    continent = np.logical_not(oceans)
    density = np.full(topography.shape, np.nan, dtype="float")
    density[continent] = density_crust
    # The minus sign is used to negate the bathymetry (which is negative and
    # the equation calls for "thickness", not height). This is more practical
    # than taking the absolute value of the topography.
    density[oceans] = -1 * (density_water - density_crust)
    bouguer = 1e5 * 2 * np.pi * GRAVITATIONAL_CONST * density * topography
    return bouguer

def atmospheric_correction(topography):
    """
    Calculates atmospheric correction as per Hinze 2005 eqn 5.
    
    .. math::

        g_{atm} = 0.874 - 9.9E-5 h + 3.56E-9 h^2 

    in which :math:`h` is the elevation of the station above the ellipsoid
    and :math:`g_{atm}` is the gravitational effect of the atmospheric the air
    mass in mGal.

    Parameters
    ----------
    topography : array or :class:`xarray.DataArray`
        Topography height and bathymetry depth in meters.
        Should be referenced to the ellipsoid (ie, geometric heights).
        

    Returns
    -------
    atmos_correction : array or :class:`xarray.DataArray`
    The gravitational effect of the atmosphere in mGal

    """
    atmos_correction = 0.874 - 9.9e-05 * topography + 3.56e-09 * topography**2
    
    return atmos_correction


def spherical_bouguer_cap_correction(topography):
    """
    Calculates spherical cap correction for the Bouguer slab as per Hinze 2013.
    
    Gravity and Magnetic Exploration, Cambridge Press 2013 
    
    .. math::

        g_{spher} =  0.001464139 h - 3.533047e-07 h^{2} + 1.002709e-13 h^{3}
        + 3.002407E-18 h^{4} 

    in which :math:`h` is the elevation of the station above the ellipsoid
    and :math:`g_{spher}` is the gravitational effect of the spherical cap to 
    166.7 km in mGal.

    Parameters
    ----------
    topography : array or :class:`xarray.DataArray`
        Topography height and bathymetry depth in meters.
        Should be referenced to the ellipsoid (ie, geometric heights).
            

    Returns
    -------
    spher_cap_corr : array or :class:`xarray.DataArray`
    The gravitational effect of the spherical cap in mGal

    """
    spher_cap_corr =  0.001464139 * topography - 3.533047e-07 * topography**2
    + 1.002709e-13 * topography**3 + 3.002407E-18 * topography**4
    
    return spher_cap_corr


def free_air_correction(topography, latitude):
    """
    Calculates free air correction as per Hinze 2005 eqn 5, including 2nd order
    terms.
    
    Note if the normal gravity is calculated using the station elevation, not
    on the ellipsoid (0 m), then the free air correction is not required.
    
    .. math::

        g_{fac} =  -(0.3087691 - 0.0004398 sin^{2}\phi)h + 7.2125E-08 h^{2}

    in which :math:`h` is the elevation of the station above the ellipsoid,
    :math: `\phi` is the station latitude and :math:`g_{fac}` is the
    gravitational effect of the "free air" in mGal.

    Parameters
    ----------
    topography : array or :class:`xarray.DataArray`
        Topography height and bathymetry depth in meters.
        Should be referenced to the ellipsoid (ie, geometric heights).
        
    latitude : array or :class:`xarray.DataArray`

    Returns
    -------
    free_air_corr : array or :class:`xarray.DataArray`
    The gravitational effect of the elevation of the station above the ellipsoid
    in the absence of topographic mass

    """  

    free_air_corr = -(0.3087691 - 0.0004398*(np.sin(np.radians(latitude)))**2) 
    * topography + 7.2125e-08 * topography**2
    
    return free_air_corr

def eotvos_correction(latitude, velocity, azimuth):
    """
    Calculates the eotvos correction for a moving gravity meter.

    Parameters
    ----------
    latitude : array or :class:`xarray.DataArray`
        
    velocity : array or :class:`xarray.DataArray`
        DESCRIPTION. in knots
        
    azimuth : array or :class:`xarray.DataArray`
        direction of movement of fhe vehicle measured clockwise from true north
    
    Returns 
    -------
    eotvos correction in mGal
    as per Blakely 1995 page 142/143

    """
    eotvos_corr = 7.503 * velocity * np.sin(np.radians(azimuth)) *
    np.cos(np.radians(latitude)) + 0.004154 * velocity**2
    
    return eotvos_corr
    
    
    
    