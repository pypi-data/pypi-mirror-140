from setuptools import setup


setup(
    name='PythonHueControl',
    version='0.4.2',
    packages=['pythonhuecontrol', 'pythonhuecontrol.v1', 'pythonhuecontrol.v1.configuration',
              'pythonhuecontrol.v1.capabilities', 'pythonhuecontrol.v1.rule', 'pythonhuecontrol.v1.group',
              'pythonhuecontrol.v1.light', 'pythonhuecontrol.v1.scene', 'pythonhuecontrol.v1.bridge',
              'pythonhuecontrol.v1.sensor', 'pythonhuecontrol.v1.schedule', 'pythonhuecontrol.v1.resourcelinks',
              'pythonhuecontrol.v2'],
    package_dir={'': '.'},
    keywords=['Hue', 'Python', 'API', 'Philips', 'Signify', 'Light', 'Sensor', 'IoT', 'Home Automation', 'Domotica'],
    url='https://github.com/elnkosc/PythonHueControl',
    license='GPL',
    author='Koen',
    author_email='koen@schilders.org',
    description='Feature Rich Python API for Hue V1 and V2',
    long_description=open('README.md', 'rt').read(),
    long_description_content_type='text/markdown'
)
