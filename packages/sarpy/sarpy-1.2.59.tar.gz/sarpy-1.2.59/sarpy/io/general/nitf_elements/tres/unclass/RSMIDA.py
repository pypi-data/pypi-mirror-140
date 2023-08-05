
from ..tre_elements import TREExtension, TREElement

__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


class RSMIDAType(TREElement):
    def __init__(self, value):
        super(RSMIDAType, self).__init__()
        self.add_field('IID', 's', 80, value)
        self.add_field('EDITION', 's', 40, value)
        self.add_field('ISID', 's', 40, value)
        self.add_field('SID', 's', 40, value)
        self.add_field('STID', 's', 40, value)
        self.add_field('YEAR', 's', 4, value)
        self.add_field('MONTH', 's', 2, value)
        self.add_field('DAY', 's', 2, value)
        self.add_field('HOUR', 's', 2, value)
        self.add_field('MINUTE', 's', 2, value)
        self.add_field('SECOND', 's', 9, value)
        self.add_field('NRG', 's', 8, value)
        self.add_field('NCG', 's', 8, value)
        self.add_field('TRG', 's', 21, value)
        self.add_field('TCG', 's', 21, value)
        self.add_field('GRNDD', 's', 1, value)
        self.add_field('XUOR', 's', 21, value)
        self.add_field('YUOR', 's', 21, value)
        self.add_field('ZUOR', 's', 21, value)
        self.add_field('XUXR', 's', 21, value)
        self.add_field('XUYR', 's', 21, value)
        self.add_field('XUZR', 's', 21, value)
        self.add_field('YUXR', 's', 21, value)
        self.add_field('YUYR', 's', 21, value)
        self.add_field('YUZR', 's', 21, value)
        self.add_field('ZUXR', 's', 21, value)
        self.add_field('ZUYR', 's', 21, value)
        self.add_field('ZUZR', 's', 21, value)
        self.add_field('V1X', 's', 21, value)
        self.add_field('V1Y', 's', 21, value)
        self.add_field('V1Z', 's', 21, value)
        self.add_field('V2X', 's', 21, value)
        self.add_field('V2Y', 's', 21, value)
        self.add_field('V2Z', 's', 21, value)
        self.add_field('V3X', 's', 21, value)
        self.add_field('V3Y', 's', 21, value)
        self.add_field('V3Z', 's', 21, value)
        self.add_field('V4X', 's', 21, value)
        self.add_field('V4Y', 's', 21, value)
        self.add_field('V4Z', 's', 21, value)
        self.add_field('V5X', 's', 21, value)
        self.add_field('V5Y', 's', 21, value)
        self.add_field('V5Z', 's', 21, value)
        self.add_field('V6X', 's', 21, value)
        self.add_field('V6Y', 's', 21, value)
        self.add_field('V6Z', 's', 21, value)
        self.add_field('V7X', 's', 21, value)
        self.add_field('V7Y', 's', 21, value)
        self.add_field('V7Z', 's', 21, value)
        self.add_field('V8X', 's', 21, value)
        self.add_field('V8Y', 's', 21, value)
        self.add_field('V8Z', 's', 21, value)
        self.add_field('GRPX', 's', 21, value)
        self.add_field('GRPY', 's', 21, value)
        self.add_field('GRPZ', 's', 21, value)
        self.add_field('FULLR', 's', 8, value)
        self.add_field('FULLC', 's', 8, value)
        self.add_field('MINR', 's', 8, value)
        self.add_field('MAXR', 's', 8, value)
        self.add_field('MINC', 's', 8, value)
        self.add_field('MAXC', 's', 8, value)
        self.add_field('IE0', 's', 21, value)
        self.add_field('IER', 's', 21, value)
        self.add_field('IEC', 's', 21, value)
        self.add_field('IERR', 's', 21, value)
        self.add_field('IERC', 's', 21, value)
        self.add_field('IECC', 's', 21, value)
        self.add_field('IA0', 's', 21, value)
        self.add_field('IAR', 's', 21, value)
        self.add_field('IAC', 's', 21, value)
        self.add_field('IARR', 's', 21, value)
        self.add_field('IARC', 's', 21, value)
        self.add_field('IACC', 's', 21, value)
        self.add_field('SPX', 's', 21, value)
        self.add_field('SVX', 's', 21, value)
        self.add_field('SAX', 's', 21, value)
        self.add_field('SPY', 's', 21, value)
        self.add_field('SVY', 's', 21, value)
        self.add_field('SAY', 's', 21, value)
        self.add_field('SPZ', 's', 21, value)
        self.add_field('SVZ', 's', 21, value)
        self.add_field('SAZ', 's', 21, value)


class RSMIDA(TREExtension):
    _tag_value = 'RSMIDA'
    _data_type = RSMIDAType
