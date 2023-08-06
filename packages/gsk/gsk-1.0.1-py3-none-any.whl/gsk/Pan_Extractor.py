"""
    Author: Deepak singh Chauhan
    Contact: deepaksingh0034602@gmail.com
    Date modified: 02-10-2021   
    Description: This script extracts Pan information from the image uploaded by consumer. The result is returned
    as a json object.
"""

import cv2
import re
import json
import easyocr


class Pan_Info_Extractor:
    def __init__(self):
        try:
            import warnings
            warnings.filterwarnings('ignore')
            self.reader = easyocr.Reader(['en'],False)
        except ImportError:
            print('No module named: easyocr')
        self.datepatn = r'\d+[-/]\d+[-/]\d+'
        self.panpatn = r'([A-Z]){5}([O0-9]){4}([A-Z]){1}'
        self.namepatn = r'([A-Z]+)\s([A-Z]+)\s([A-Z]+)'
        self.fnamepatn = r'([A-Z]+)\s+?'
        self.godpatn = r'([A-Z]+)\s([A-Z]+)\s([A-Z]+)$|([A-Z]+)\s([A-Z]+)$'

    def info_extractor(self, image_file):
        """Function to extract information from the pan card image

        Args:
                ocr_text (list): text from the ocr

        Returns:
                json: Data extracted from pan card image
        """
        self.PAN = 'NAN'
        self.Name = 'NAN'
        self.FatherName = 'NAN'
        self.DOB = 'NAN'
        self.image = image_file
        img = cv2.imread(self.image)
        OCR_text = self.reader.readtext(img, detail=0, width_ths=0.9)
        # print(OCR_text)

        gov = [i for i, txt in enumerate(OCR_text) if 'GOVT' in txt][0]
        OCR_text = OCR_text[gov + 1:]
        temp = []
        for text in OCR_text:
            name = re.search(self.godpatn, text)
            # print(name.group())
            if name:
                temp.append(name.group())
        
        #Handle 'O's in Digits
        temp = ''
        for i,char in enumerate(self.PAN):
            if i>4 and i<9:
                if char == 'O':
                    char = '0'
            temp = temp+char
        self.PAN = temp
        # print(self.PAN)

        if self.Name == 'NAN':
            self.Name = temp[0]
        if self.FatherName == 'NAN':
            self.FatherName = temp[1]

        for text in OCR_text:
            if self.PAN == 'NAN' and re.search(self.panpatn, text):
                self.PAN = re.search(self.panpatn, text).group()
                break

        for text in OCR_text:
            if self.DOB == 'NAN' and re.search(self.datepatn, text):
                self.DOB = re.search(self.datepatn, text).group()
                break

        extracted = {
            'Pan_number': self.PAN,
            'Name': self.Name,
            'Father_Name': self.FatherName,
            'DOB': self.DOB
        }

        return json.dumps(extracted)