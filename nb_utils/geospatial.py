from numpy import arcsin, cos, radians, sin, sqrt

def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371000):
    """Vectorized great circle distance between two points

    lat, lon: specified in decimal degrees or in radians
    returns: distance in meters
    """

    if to_radians:
        lat1, lon1, lat2, lon2 = radians([lat1, lon1, lat2, lon2])

    a = (sin((lat2-lat1)/2.0)**2 +
         cos(lat1) * cos(lat2) * sin((lon2-lon1)/2.0)**2)

    return earth_radius * 2 * arcsin(sqrt(a))
