import os

from astropy.io import fits
import pyregion

from wfc3tools.calwf3 import calwf3


def ir_satmask(raw_filename, region_filename, imset):
    """
    Mask satellite trails in the DQ array of individual IMA read.

    Note that if the raw file is part of an association, the .asn file must be
    in the same directory as the raw file.

    Parameters
    ----------
    raw_input : str
        Input raw file to be sattelite corrected

    region_filename: str
        Input region file name. Expecting DS9 style region file

    imset: int
        Imset (Read number) that needs to be satellite corrected.

    """

    raw = fits.open(raw_filename, mode='update')
    orig_crcorr = raw[0].header['CRCORR']
    raw[0].header['CRCORR'] = 'OMIT'
    raw.flush()
    raw.close()

    calwf3(raw_filename)

    # rename ima file
    os.rename(raw_filename.replace("raw", "ima"),
              raw_filename.replace("raw", "ima_temp"))
    temp_filename = raw_filename.replace("raw", "ima_temp")

    # delete interim flt file
    os.remove(raw_filename.replace("raw", "flt"))

    # reset CRCORR to original value in raw
    raw = fits.open(raw_filename, mode='update')
    raw[0].header['CRCORR'] = orig_crcorr
    raw.close()

    # Apply region mask
    hdu = fits.open(temp_filename, mode='update')
    hdu[0].header['CRCORR'] = 'PERFORM'
    # ext = ((imset-1) * 5) + 3
    # reg = pyregion.open(region_filename).as_imagecoord(hdu[ext].header)
    # mask = reg.get_mask(shape=(1024, 1024))
    # hdu[ext].data[mask] |= 16384
    hdu.close()

    # Finishing running calwf3
    calwf3(temp_filename)



