# Optix
Library that simplifies matrix optics calculations.

## Key features
  - Provides plenty of optical elements
  - Simulates propagating through the optical system and prints out the resultant gaussian beam

# TO-DO
  - Add optimization module to iterate though possible optical system compositions and choose the most favourable one 
  - Support non-Gaussian beams
  - Prints out the scheme of the system
  - Prints out the gaussian beam transformation
  - ... ?

## Usage
```Python
from optix.ABCDformalism *

# Alongside with wavelnegth one aditional parameter needs to be specified. Reyleigh range (zr), divergence (div) or waist radius (w0)
input = GaussianBeam(wavelength=405e-9, zr=0.01)

op = OpticalPath()
op.append(FreeSpace(d=0.1))
op.append(ThinLens(d=2.5e-2))
op.append(ThickLens(R1=0.8, n=1.2, R2=0.4, d=0.01))
op.append(FreeSpace(d=1))

# Outpus gaussian Beam
output = op.propagate(input)
print(output)
```
## Installation
```
pip install optix
```
