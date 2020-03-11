import pyexiv2 as ev
import math

def to_deg(value, loc):
    """convert decimal coordinates into degrees, minutes and seconds tuple
    value: float gps-value
    loc: direction list ["S", "N"] or ["W", "E"]
    return: degree location tuple
    e.x. to_deg(121.683333333, ["W", "E"])
         >>(121, 41, 0 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value * 60 - deg * 60)
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    if sec == 60:
        sec = 0
        min += 1
    return (deg, min, sec, loc_value)

def to_decimal(frac_deg):
    """
    convert degrees, minutes and seconds tuple to decimal coordinates
    frac_deg is in format: (fraction(deg + min / 60), fraction(sec / 60), fraction(0, 1))
    return: decimal location
    e.x. to_decimal([Fraction(7273, 60), Fraction(7, 15), Fraction(0, 1)])
         >>121.683333333
    """
    return (frac_deg[0] + frac_deg[1] / 60) * 1.0

def check_location(file_name):
    """
    check if a photo has gps info
    YES: return (latitude, longitude)
    No: return none
    """
    try:
        exiv_image = ev.ImageMetadata(file_name)
        exiv_image.read()
        exiv_lat = exiv_image["Exif.GPSInfo.GPSLatitude"]
        exiv_lng = exiv_image["Exif.GPSInfo.GPSLongitude"]
        if exiv_lat.value[0] < 1:
            return (0, 0)
        return (to_decimal(exiv_lng.value), to_decimal(exiv_lat.value))
    except:
        return (0, 0)

# check_location('photos/IMG_5720.jpg')

def set_gps_location(file_name, lat, lng):
    """Adds GPS position as EXIF metadata
    file_name: image file
    lat: latitude (as float)
    lng: longitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])
    # if alt < 0:
    #     alt_deg = (alt, bytes(1))
    # else:
    #     alt_deg = (alt, bytes(0))

    print(lat_deg)
    print(lng_deg)
    # print alt_deg

    # class pyexiv2.utils.Rational(numerator, denominator) => convert decimal coordinates into degrees, minutes and seconds
    exiv_lat = (ev.Rational(lat_deg[0] * 60 + lat_deg[1], 60),ev.Rational(lat_deg[2]*10000,600000), ev.Rational(0, 1))
    exiv_lng = (ev.Rational(lng_deg[0] * 60 + lng_deg[1], 60),ev.Rational(lng_deg[2]*10000,600000), ev.Rational(0, 1))
    # exiv_alt = (ev.Rational(alt * 1000, 1000))

    exiv_image = ev.ImageMetadata(file_name)
    exiv_image.read()

    # modify GPSInfo of image
    exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
    exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
    # exiv_image["Exif.GPSInfo.GPSAltitude"]= exiv_alt
    # exiv_image["Exif.GPSInfo.GPSAltitudeRef"] = alt_deg[1]
    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 2 0 0'

    exiv_image.write()

# set_gps_location('IMG_5124.JPG', 30.22222, 110.22222)