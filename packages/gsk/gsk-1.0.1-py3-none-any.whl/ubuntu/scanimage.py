from awgp.ubuntu.shell import Shell
import numpy as np
import cv2
class ScanImage:
    def __iniit__(self):
        self.message = ""
        pass

    def getDeviceList(self):
        cmd = ""
        output = Shell.run("scanimage -L").decode("utf-8")
        output = str(output).split("\n")
        
        dsl = []
        for o in output:
            oo = o.split("is a")
            if len(oo)>1:

                oo[0] = oo[0].replace("device ","").replace("`","").replace("'","").strip()
                oo[1] = oo[1].replace("'","").strip()
                ox = {"code":oo[0],"name":oo[1]}
                dsl.append(ox)
        return ox
        
    def removeWhightSpace(self,filename):
        

        img = cv2.imread(filename) # Read in the image and convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = 255*(gray < 128).astype(np.uint8) # To invert the text to white
        coords = cv2.findNonZero(gray) # Find all non-zero points (text)
        x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
        rect = img[y:y+h, x:x+w] # Crop the image - note we do this on the original image
        # cv2.imshow("Cropped", rect) # Show it
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        cv2.imwrite(filename, rect)
        return filename
    def scanImage(self,id,output):
        tmp = "tmp"
        # cmd = f'exec 2>&1; scanimage --resolution 100 --mode "24 bit Color" -d "{id}" --format=tiff | convert - -set {output}: "%t" %[{output}:].jpg'
        cmd = f'scanimage --resolution 150 --mode "24 bit Color" -d "{id}" --format jpeg  --source "Automatic Document Feeder(left aligned,Duplex)" --batch=tmp/scan%04d.jpg --batch-count='
        sOut = Shell.runSystem(cmd)
        if sOut!="":
            self.message = sOut
            return None
        else:
            r = []
            output = "tmp/scan0001.jpg"
            output = self.removeWhightSpace(output)
            # Shell.runSystem(f"convert -i {output} {output}.jpg")
            r.append("scan0001.jpg")
            output = "tmp/scan0002.jpg"
            output = self.removeWhightSpace(output)
            # Shell.runSystem(f"convert -i {output} {output}.jpg")
            r.append("scan0002.jpg")
            # self.removeWhightSpace(output)
            return r
        