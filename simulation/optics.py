import numpy as np
from chroma.geometry import Material, Surface

# Materials
"""
    list of optical properties:
        self.refractive_index = None
        self.absorption_length = None
        self.scattering_length = None
        self.scintillation_spectrum = None
        self.scintillation_light_yield = None
        self.scintillation_waveform = None
        self.scintillation_mod = None
        self.comp_reemission_prob = []
        self.comp_reemission_wvl_cdf = []
        self.comp_reemission_times = []
        self.comp_reemission_time_cdf = []
        self.comp_absorption_length = []
        self.density = 0.0 # g/cm^3
        self.composition = {} # by mass
"""
standard_wavelengths = np.arange(60, 1000, 5).astype(np.float32)
# all material/surface properties are interpolated at these
# wavelengths when they are sent to the gpu

vacuum = Material('vacuum')
vacuum.set('refractive_index', 1.0)
vacuum.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
vacuum.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))

cf4 = Material('cf4')
cf4.density = 3.72
cf4.composition = { 'H' : 0.1119, 'O' : 0.8881 } # fraction by mass
cf4.set('refractive_index', 1.22)
cf4.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
cf4.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))

sapphire = Material('sapphire')
sapphire.set('refractive_index', 1.22)
sapphire.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
sapphire.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))

quartz = Material('quartz')
quartz.set('refractive_index', 1.46)
#quartz.absorption_length = \
#    np.array([(200, 0.1e-6), (300, 0.1e-6), (330, 1000.0), (500, 2000.0), (600, 1000.0), (770, 500.0), (800, 0.1e-6), (1000, 0.1e-6)])
quartz.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
quartz.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))


argon = Material('argon')
argon.density = 1.40
argon.set('refractive_index', 1.17)
argon.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
argon.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))

bubblegas = Material('bubblegas')
bubblegas.density = 1.40
bubblegas.set('refractive_index', 1.00)
bubblegas.set('absorption_length', np.repeat(1e6,len(standard_wavelengths)))
bubblegas.set('scattering_length', np.repeat(1e6,len(standard_wavelengths)))

# Surfaces
black_surface = Surface('black_surface')
black_surface.set('absorb', 1)
# same as chroma/demo, used at SiPM and Steel


# The reflector surface used for normal simulations
teflon_surface = Surface('teflon_surface')
teflon_surface.set('absorb', 0.1)
teflon_surface.set('reflect_diffuse', 0.9)

reflector_surface = Surface('reflector_surface')
reflector_surface.set('reflect_diffuse', 0.9)
reflector_surface.set('absorb', 0.1)

detector_surface = Surface('detector_surface')
detector_surface.detect = np.array([(400,0.1), (1000,0.1)])
detector_surface.set('reflect_diffuse', 0.9)
# chroma will do linear interpolation for the detection rate

"""
for more parameters and details concerning optics, refer to chroma/demo/optics
"""