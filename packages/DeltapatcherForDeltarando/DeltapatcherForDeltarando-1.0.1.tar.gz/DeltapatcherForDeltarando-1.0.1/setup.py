from setuptools import setup, find_packages

VERSION = '1.0.1' 
DESCRIPTION = 'DELTARUNE Randovania Patcher'
LONG_DESCRIPTION = 'The patcher for the DELTARUNE Randovania addition. '

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="DeltapatcherForDeltarando", 
        version=VERSION,
        author="jonloveslegos",
        author_email="<jonloveslegos@email.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=[],
        classifiers= []
)