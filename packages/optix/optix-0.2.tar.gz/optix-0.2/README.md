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

input = GaussianBeam(wavelength=405e-9, zr=0.01)

op = OpticalPath()
op.append(FreeSpace(0.1))
op.append(ThinLens(2.5e-2))
op.append(ThickLens(0.8, 1.2, 0.4, 0.01))
op.append(FreeSpace(1))

output = op.propagate(input)
print(output)
```
## Installation
```
pip install optix
```
