"""
Point Mass Forward Modelling on Cartesian Coordinates
=====================================================

The simplest geometry used to compute gravitational fields are point masses.
Although modelling geologic structures with point masses can be challenging, they are
very usefull for other purposes: creating synthetic models, solving inverse problems
very quickly, generating equivalent sources for interpolation or gridding, etc.
Besides, the gravitational fields generated by point masses can be quickly computed
either in Cartesian or in geocentric spherical coordinate system.
We will compute the downward component of the gravitational acceleration generated by
a set of point masses on a computation grid given in Cartesian coordinates. We will do
it throught the :func:`harmonica.point_mass_gravity` function.
"""
import harmonica as hm
import verde as vd
import matplotlib.pyplot as plt
import matplotlib.ticker


# Define two point masses with oposite mass values of 10000000 kg
easting = [5e3, 15e3]
northing = [5e3, 15e3]
vertical = [-5e3, -2.5e3]
points = [easting, northing, vertical]
masses = [10e6, -10e6]

# Define computation points on a grid at 500m above the ground
coordinates = vd.grid_coordinates(
    region=[0, 20e3, 0, 20e3], shape=(80, 80), extra_coords=500
)

# Compute the downward component of the acceleration
gravity = hm.point_mass_gravity(
    coordinates, points, masses, field="g_z", coordinate_system="cartesian"
)
print(gravity)

# Plot the gravitational field
fig, ax = plt.subplots(figsize=(8, 9))
ax.set_aspect("equal")
img = plt.pcolormesh(*coordinates[:2], gravity)
# Add colorbar
fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
fmt.set_powerlimits((0, 0))
plt.colorbar(img, ax=ax, format=fmt, pad=0.04, shrink=0.73, label="mGal")
ax.set_title("Downward component of gravitational acceleration")
# Convert axes units to km
ax.set_xticklabels(ax.get_xticks() * 1e-3)
ax.set_yticklabels(ax.get_yticks() * 1e-3)
ax.set_xlabel("km")
ax.set_ylabel("km")
plt.show()
