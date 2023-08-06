from setuptools import setup, find_packages

VERSION = '0.1.3' 
DESCRIPTION = 'Lots of simple acoustics calculations, all in one place.'
LONG_DESCRIPTION = 'This is a package that I am writing during my time as a graduate student at Brigham Young University. My research is in aeroacoustics, and most of our code is written in MATLAB. Knowing that I may not always have access to MATLAB, and because I enjoy open-source software, I\'ve decided to create code in Python that performs many of the same tasks that we regularly perform for research. My dream is that this package can develop to the point where it could realistically be used to do all of the same research that we currently perform in MATLAB.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="acousticspy", 
        version=VERSION,
        author="Mark C. Anderson",
        author_email="anderson.mark.az@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(exclude=['tests']),
        install_requires=['numpy','scipy','matplotlib'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'acoustics'],
        classifiers= [
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "License :: OSI Approved :: MIT License",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Physics"
        ]
)
