#!/usr/bin/env python
# encoding: utf-8
"""
dentistdataconv.py

dentistdataconv.py is a simple Python script that converts volumetric dentist
data to better documented volume formats: [nrrd][1], [MetaImage (mhd)][2], and
[nifti (nii)][3].

[1]: http://teem.sourceforge.net/nrrd/
[2]: http://www.itk.org/Wiki/MetaIO/
[3]: http://nifti.nimh.nih.gov/nifti-1/

Created by Maarten H. Everts
License: see LICENSE (MIT).
"""

import sys
import os
import numpy as np
import gzip
from xml.dom.minidom import parseString
from optparse import OptionParser
try:
    from nifti import NiftiImage
except Exception, e:
    print "Warning: pynifti not found, .nii output not supported."

def read_slice(filename, slice_dim):
    """Read slice of data from file, return numpy array with data"""
    # The data is stored in a collection of gzipped files containing
    # raw 16 bit little endian integers.
    with open(filename,'rb') as f:
        gzipfile = gzip.GzipFile(fileobj=f)
        return np.fromstring(gzipfile.read(), np.int16).reshape(slice_dim)

__cached_data__ = None

def get_data(settings):
    """Return volume data as numpy array. Caches the data."""
    global __cached_data__
    if __cached_data__ is None:
        slice_filenames = [settings['settings_filename'] + '_' + "%03d" % i \
                            for i in range(int(settings['VolSizeZ']))]
        slice_dim = (int(settings['VolSizeX']), int(settings['VolSizeY']))
        print "Reading data from the slices."
        slices = [read_slice(filename, slice_dim) for filename in slice_filenames]
        # This step of combining all the slices to one numpy array is not very
        # memory efficient, but for now it is good enough.
        print "Combining the slices into a single volume."
        __cached_data__ = np.array(slices)
    return __cached_data__
    
def write_metaimage_header(settings, basename):
    """Write a metaimage header to <basename>.mhd."""
    header = ['NDims = 3',
              'DimSize = %(VolSizeX)s %(VolSizeY)s %(VolSizeZ)s' % settings,
              'ElementType = MET_USHORT',
              'ElementSize = %(VoxelSizeX)s %(VoxelSizeY)s %(VoxelSizeZ)s' % settings,
              'ElementDataFile = '+basename+'.raw',
              '']
    filename = basename+'.mhd'
    print 'Writing metaimage header to '+filename+'.'
    with open(filename, 'wt') as f:
        f.write('\n'.join(header))

def write_nrrd_header(settings, basename):
    """Write an nrrd header to <basename>.nhdr."""
    header = ['NRRD0001',
            '# Complete NRRD file format specification at:',
            '# http://teem.sourceforge.net/nrrd/format.html',
            'content: volume',
            'type: unsigned short',
            'dimension: 3',
            'sizes: %(VolSizeX)s %(VolSizeY)s %(VolSizeZ)s' % settings,
            'spacings: %(VoxelSizeX)s %(VoxelSizeY)s %(VoxelSizeZ)s' % settings,
            'data file: '+basename+'.raw',
            '']
    filename = basename+'.nhdr'
    print 'Writing nrrd header to '+filename+'.'            
    with open(filename, 'wt') as f:
        f.write('\n'.join(header))

def write_raw_file(settings, basename):
    """Write raw data to <basename>.raw."""
    volume_data = get_data(settings)
    filename = basename+'.raw'
    print 'Writing raw data to '+filename+'.'
    volume_data.tofile(filename)

def write_nifti_file(settings, basename):
    """Write data <basename>.nii."""
    nim = NiftiImage(get_data(settings))
    filename = basename+'.nii'
    print 'Writing data to the nifti file '+filename+'.'    
    nim.save(filename)

def get_settings(input_path):
    """Read settings from xml file."""
    input_path = os.path.normpath(input_path)
    if not os.path.isdir(input_path):
        raise RuntimeError("Expected a directory.")
    base_name = os.path.split(input_path)[1]
    # The settings file (a gzipped XML file) has the same name as
    # the directory.
    settings_filename = os.path.join(input_path, base_name)
    with open(settings_filename, 'rb') as f:
        gzipfile = gzip.GzipFile(fileobj=f)
        settings_dom = parseString(gzipfile.read())
        # Only a particular part of the XML file is interesting, create
        # a dictionary for it.
        params_node = settings_dom.getElementsByTagName('FBPParams')[0].\
                                   getElementsByTagName('LibParams')[0]
        settings = dict([(str(n.nodeName), str(n.childNodes[0].data)) for n in \
                params_node.childNodes if len(n.childNodes) == 1])
        # The settings filename is used by get_data to determine the filenames
        # of the slices.
        settings['settings_filename'] = settings_filename
        return settings

def main():
    usage = "usage: %prog [options] inputdirectory outputbasename"
    parser = OptionParser(usage)
    parser.add_option('-n', '--nhdr', dest='outputtypes', action='append_const',
                      const='nhdr', help='write nrrd header (nhdr)')
    parser.add_option('-m', '--metaimage', dest='outputtypes', action='append_const',
                      const='mhd', help='write metaimage header (mhd)')
    parser.add_option('-i', '--nifti', dest='outputtypes', action='append_const',
                      const='nii', help='write nifti file (nii)')        
    parser.add_option('-r', '--raw', dest='outputtypes', action='append_const',
                      const='raw', help='write raw data to file (used by header files)')
            
    (options, args) = parser.parse_args()
    if options.outputtypes is None:
        parser.error('Need atleast one output type.')
    if len(args) == 1:
        parser.error('Missing basename for output.')
    elif len(args) > 2:
        parser.error('Too many arguments, need two.')
    
    inputdirectory = args[0]
    outputbasename = args[1]
    settings = get_settings(inputdirectory)
    
    output_mapping = {'nhdr': write_nrrd_header,
                      'mhd':  write_metaimage_header,
                      'nii':  write_nifti_file,
                      'raw':  write_raw_file
                     }
    for outputtype in options.outputtypes:
        output_mapping[outputtype](settings, outputbasename)
    print 'Done.'


if __name__ == "__main__":
    sys.exit(main())
