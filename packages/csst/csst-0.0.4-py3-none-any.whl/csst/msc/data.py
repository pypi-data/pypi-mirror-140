from collections import OrderedDict
import astropy.io.fits as fits
from astropy.io.fits import HDUList, PrimaryHDU, ImageHDU
from astropy.io.fits.header import Header
from ..common.data import CsstData, INSTRUMENT_LIST


__all__ = ["CsstMscData", "CsstMscImgData"]


class CsstMscData(CsstData):
    _l1img_types = {'sci': True, 'weight': True, 'flag': True}

    def __init__(self, priHDU, imgHDU, **kwargs):
        super(CsstData, self).__init__(priHDU, imgHDU, **kwargs)
        self._l1hdr_global = priHDU.header.copy()
        #         self._l1hdr_global['SIMPLE']  =  'T' #/ conforms to FITS standard
        #         self._l1hdr_global['NAXIS']  =  0kkjk
        self._l1data['sci'] = ImageHDU()
        self._l1data['weight'] = ImageHDU()
        self._l1data['flag'] = ImageHDU()

    def set_flat(self, flat):
        """ set flat

        Parameters
        ----------
        flat:
            flat image

        Returns
        -------

        """
        self._auxdata['flat'] = flat

    def set_bias(self, biasimg):
        self._auxdata['bias'] = biasimg

    def set_dark(self, darkimg):
        self._auxdata['dark'] = darkimg

    def set_badpixel(self, badpixelimg):
        self._auxdata['badpixel'] = badpixelimg

    def get_flat(self):
        return self._auxdata['flat']

    def get_bias(self):
        return self._auxdata['bias']

    def get_dark(self):
        return self._auxdata['dark']

    def get_badpixel(self):
        return self._auxdata['badpixel']

    def init_l0data(self):
        pass

    def set_l1keyword(self, key, value, comment=''):
        print('check out whether ' + key + " is a valid key and " + value + " is valid value")
        self._l1hdr_global.set(key, value, comment)

    def set_l1data(self, imgtype, img):
        try:
            if self._l1img_types[imgtype]:
                self._l1data[imgtype].data = img.copy()
        except Exception as e:
            print(e)
        print('save image data to l1data')

    def save_l1data(self, imgtype, filename):
        print('check ' + imgtype + ' is validate')
        try:
            if self._l1img_types[imgtype]:
                super().save_l1data(imgtype, filename)
        except Exception as e:
            print(e)


class CsstMscImgData(CsstMscData):
    def __init__(self, priHDU, imgHDU, **kwargs):
        # print('create CsstMscImgData')
        super(CsstMscData, self).__init__(priHDU, imgHDU, **kwargs)

    def __repr__(self):
        return "<CsstMscImgData: {} {}>".format(self.instrument, self.detector)

    @staticmethod
    def read(fp):
        """ read from fits file

        Parameters
        ----------
        fp:
            the file path of fits file

        Returns
        -------
        CsstMscImgData

        """

        try:
            hl = fits.open(fp)
            instrument = hl[0].header.get('INSTRUME')  # strip or not?
            detector = hl[0].header.get('DETECTOR')  # strip or not?
            print("@CsstMscImgData: reading data {} ...".format(fp))
            assert instrument in INSTRUMENT_LIST
            if instrument == 'MSC' and 6 <= int(detector[3:5]) <= 25:
                # multi-band imaging
                data = CsstMscImgData(hl[0], hl[1], instrument=instrument, detector=detector)
                return data
        except Exception as e:
            print(e)
