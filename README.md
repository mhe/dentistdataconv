dentistdataconv
===============

dentistdataconv.py is a simple Python script that converts volumetric dentist
data to better documented volume formats: [nrrd][1], [MetaImage (mhd)][2], and
[nifti (nii)][3].

[1]: http://teem.sourceforge.net/nrrd/
[2]: http://www.itk.org/Wiki/MetaIO
[3]: http://nifti.nimh.nih.gov/nifti-1/

Dependencies
------------

Besides Python, the script's only dependency is [numpy][4]. For nifti (.nii)
output one also needs [pynifti][5].

[4]: http://numpy.scipy.org/
[5]: http://niftilib.sourceforge.net/pynifti/

Usage
-----

The -h options shows how to use it:

    Usage: dentistdataconv.py [options] inputdirectory outputbasename
    
    Options:
      -h, --help       show this help message and exit
      -n, --nhdr       write nrrd header (nhdr)
      -m, --metaimage  write metaimage header (mhd)
      -i, --nifti      write nifti file (nii)
      -r, --raw        write raw data to file (used by header files)

For example, the following command, 

    ./dentistdataconv.py -n -m -r /path/to/datadirectory myvolume

will produce three files:
    myvolume.nrrd
	myvolume.mhd
	myvolume.raw

License
-------

See LICENSE.
