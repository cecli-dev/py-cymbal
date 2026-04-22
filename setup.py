from setuptools import setup
from setuptools.dist import Distribution
import os

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            super().finalize_options()
            self.root_is_pure = False
        def get_tag(self):
            python, abi, plat = super().get_tag()
            return 'py3', 'none', plat
    cmdclass = {'bdist_wheel': bdist_wheel}
except ImportError:
    cmdclass = {}

class BinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True

plat_name = os.environ.get('WHEEL_PLATFORM_NAME', 'any')

setup(
    distclass=BinaryDistribution,
    cmdclass=cmdclass,
    options={'bdist_wheel': {'plat_name': plat_name}}
)
