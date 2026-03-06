---
permalink: /en/resources-tools/datasets/
---

# Dataset Downloads

> Author: [CislunarSpace](https://gitee.com/cislunarspace)
>
> Website: [https://cislunarspace.cn](https://cislunarspace.cn)

## JPL Ephemeris

### DE Series Ephemeris Introduction
The JPL Ephemeris (Development Ephemerides) is high-precision planetary and lunar position data published by the Jet Propulsion Laboratory, widely used in deep space exploration missions.

### Available Versions

#### DE405 (Recommended for Earth-Moon Missions)
- **Time Coverage**: 1600–2200
- **Accuracy**: Lunar position accuracy ~2–5 meters
- **Use Cases**: Most cislunar space mission analysis
- **Download Links**:
  ```bash
  # Official FTP download
  ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de405/
  
  # Mirror
  https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/
  ```

#### DE421
- **Time Coverage**: 1900–2050
- **Accuracy**: Lunar position accuracy ~1 meter
- **Features**: Includes more asteroid data
- **Download Links**:
  ```bash
  ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de421/
  ```

#### DE430 (Latest Version)
- **Time Coverage**: 1550–2650
- **Accuracy**: Lunar position accuracy ~0.5 meters
- **Features**: Includes lunar libration data
- **Download Links**:
  ```bash
  ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de430/
  ```

### Data Format Description

#### ASCII Format
```plaintext
# DE405 header information example
*******************************************************************************
*    Copyright (C) 1991-2005 California Institute of Technology, Pasadena, CA *
*    All rights reserved.                                                     *
*******************************************************************************
*  Start Epoch: JD 2305424.50 (1599 DEC 09)                                  *
*  Final Epoch: JD 2525008.50 (2201 FEB 20)                                  *
*  Interval   : 4.0 days                                                     *
*******************************************************************************
```

#### Binary SPK Format
```bash
# SPK file download
https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de405.bsp
```

### Usage Examples

#### Reading DE Ephemeris with Python
```python
import numpy as np
from astropy.time import Time
import jplephem

# Load DE405 ephemeris
eph = jplephem.Ephemeris('de405.bsp')

# Calculate Earth-Moon position
jd = Time('2025-01-01').jd  # Julian Date

# Earth position (relative to Solar System Barycenter)
earth_pos = eph.position('earth', jd)

# Moon position (relative to Earth)
moon_pos = eph.position('moon', jd)

print(f"Earth position: {earth_pos} km")
print(f"Moon position: {moon_pos} km")
```

#### Reading DE Ephemeris with MATLAB
```matlab
% Using MATLAB Aerospace Toolbox
jd = juliandate(datetime(2025,1,1));

% Read planetary positions
[earth_pos, earth_vel] = planetEphemeris(jd, 'Sun', 'Earth', '405');
[moon_pos, moon_vel] = planetEphemeris(jd, 'Earth', 'Moon', '405');

disp(['Earth position: ', num2str(earth_pos), ' km']);
disp(['Moon position: ', num2str(moon_pos), ' km']);
```

## Lunar Gravity Field Models

### Model Overview
Lunar gravity field models are used to accurately calculate the lunar gravitational potential, which is crucial for lunar orbit design and maintenance.

### Main Models

#### GRGM Series (GRAIL Mission)
- **GRGM900C**: Degree and order 900, spatial resolution ~5.6 km
- **GRGM1200A**: Degree and order 1200, spatial resolution ~4.2 km
- **GRGM660PRIM**: Degree and order 660, optimized for polar regions

#### GL Series (Historical Models)
- **GL0660B**: Degree and order 660, based on historical data
- **GL0900D**: Degree and order 900, combining multiple data sources

#### SGM Series (Japanese Models)
- **SGM100i**: Degree and order 100, based on Kaguya data
- **SGM150i**: Degree and order 150, higher precision version

### Download Links

#### NASA PDS Archive
```bash
# GRAIL gravity field models
https://pds-geosciences.wustl.edu/grail/grail-l-lgrs-5-gravity-v1/

# Latest models
https://pgda.gsfc.nasa.gov/products/71
```

#### ISDC Data Portal
```bash
# European data archive
https://ssedata.gsfc.nasa.gov/archive/grail/
```

### Data Format

#### Spherical Harmonic Coefficient Files
```plaintext
# GRGM900C header example
Product_id           = "GRGM900C"
Model_name           = "GRGM900C"
Maximum_degree       = 900
Maximum_order        = 900
Reference_radius     = 1738000.0
Gm                   = 4902.80007
Background_model     = "LP165P"
Data_span_start      = 2012-03-01
Data_span_end        = 2012-12-31

# Coefficient data
degree order C_nm S_nm sigma_C sigma_S
2      0     -0.000909927 0.0 1.2e-10 0.0
2      1     0.000209148 0.000199979 2.3e-10 2.3e-10
2      2     0.000227744 -0.000259674 1.8e-10 1.8e-10
```

### Usage Examples

#### Computing Lunar Gravity with Python
```python
import numpy as np
import pyshtools

# Load gravity field model
clm, slm = pyshtools.shio.read_shcoeffs('GRGM900C.gfc')

# Calculate gravitational acceleration at a point
lat = 0.0    # Latitude (degrees)
lon = 0.0    # Longitude (degrees)
r = 1738.0   # Radius (km)

# Calculate gravitational potential
potential = pyshtools.expand.MakeGridPoint(clm, slm, lat, lon, r)

# Calculate gravitational acceleration
g_lat, g_lon, g_r = pyshtools.expand.MakeGradientGridPoint(clm, slm, lat, lon, r)

print(f"Gravitational potential: {potential} m²/s²")
print(f"Gravitational acceleration: [{g_lat}, {g_lon}, {g_r}] m/s²")
```

## Space Environment Parameters

### Solar Radiation Data

#### Solar Constant
- **Average**: 1361 W/m²
- **Variation Range**: ±0.1%
- **Data Sources**: SORCE/TIM, TSIS-1

#### Download Links
```bash
# NASA Solar Radiation Data
https://lasp.colorado.edu/lisird/data/

# Historical Data
https://www.ncei.noaa.gov/products/climate-data-records/solar-irradiance
```

### Geomagnetic Field Models

#### IGRF Model
- **International Geomagnetic Reference Field**: Updated every 5 years
- **Degree**: 13 (1900–2020)
- **Accuracy**: ~50 nT

#### WMM Model
- **World Magnetic Model**: Updated every 5 years
- **Coverage**: Global
- **Accuracy**: Better than 100 nT

#### Download Links
```bash
# IGRF Model
https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html

# WMM Model
https://www.ncei.noaa.gov/products/world-magnetic-model
```

### Upper Atmosphere Models

#### NRLMSISE-00
- **Altitude Coverage**: 0–1000 km
- **Parameters**: Temperature, density, composition
- **Applicability**: Earth orbit missions

#### JB2008
- **Improved Version**: Includes solar activity effects
- **Accuracy**: Better than 15%
- **Applicability**: Long-term orbit decay prediction

#### Download Links
```bash
# CelesTrak Atmospheric Models
https://celestrak.org/SpaceData/

# NASA Space Weather Data
https://omniweb.gsfc.nasa.gov/
```

### Usage Examples

#### Computing Atmospheric Density
```python
import numpy as np
from spaceweather import sw_download
import msise00

# Download space weather data
sw_download.download_sw()

# Set parameters
alt = 400  # Altitude (km)
lat = 30   # Latitude (degrees)
lon = 120  # Longitude (degrees)
year = 2025
doy = 1    # Day of year
sec = 0    # Seconds

# Calculate atmospheric density
density = msise00.run(year, doy, sec, alt, lat, lon, 0, 0, 
                      f107=150, f107a=150, ap=4)

print(f"Atmospheric density: {density['Total']} kg/m³")
```

## Data Usage Guide

### Data Preprocessing

#### Format Conversion
```python
# Convert ASCII ephemeris to binary
from jplephem import ascii2bin

ascii2bin.convert('de405.asc', 'de405.bsp')
```

#### Data Verification
```python
# Check data integrity
import hashlib

def verify_file(filepath, expected_md5):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    if file_hash == expected_md5:
        print("File verification passed")
        return True
    else:
        print(f"File verification failed: {file_hash} != {expected_md5}")
        return False
```

### Best Practices

#### Data Management
1. **Version Control**: Record the data version used
2. **Backup Strategy**: Multiple backups for important data
3. **Metadata Logging**: Record data sources and processing steps

#### Performance Optimization
```python
# Use memory mapping for improved large file reading performance
import numpy as np

# Memory-mapped reading
data = np.memmap('large_data.bin', dtype='float64', mode='r')
```

### FAQ

#### Handling Missing Data
```python
def handle_missing_data(data, method='interpolate'):
    """
    Handle missing data
    """
    if method == 'interpolate':
        # Linear interpolation
        return np.interp(
            np.arange(len(data)),
            np.where(~np.isnan(data))[0],
            data[~np.isnan(data)]
        )
    elif method == 'forward_fill':
        # Forward fill
        mask = np.isnan(data)
        idx = np.where(~mask, np.arange(len(data)), 0)
        np.maximum.accumulate(idx, out=idx)
        return data[idx]
```

#### Data Update Strategy
```bash
# Automated update script example
#!/bin/bash
# Weekly update of space weather data
wget -q -O f107.txt https://omniweb.gsfc.nasa.gov/cgi/nx1.cgi
# Process and store data
python process_spaceweather.py f107.txt
```

### Resource Links

#### Official Data Portals
- [NASA Planetary Data System](https://pds.nasa.gov/)
- [ESA Science Data Centre](https://www.cosmos.esa.int/)
- [JAXA Data Archive](https://data.darts.isas.jaxa.jp/)

#### Community Resources
- [Space Data Sharing Platform](https://spacedata.org/)
- [Astrodynamics Data Exchange](https://astrodynamics.org/data/)
- [Open Science Data Repository](https://zenodo.org/)

#### Software Tools
- [SPICE Toolkit](https://naif.jpl.nasa.gov/naif/toolkit.html)
- [HORIZONS System](https://ssd.jpl.nasa.gov/horizons/)
- [GMAT Data Interface](https://github.com/NASA-AMMOS/GMAT/wiki/Data-Interfaces)

---

*For more datasets and updates, please follow the latest developments on this site...*
