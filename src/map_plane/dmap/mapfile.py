"""
RSA 27/05/26
Loads a ccp4 format file from disk

"""
from map_plane.dmap import mapfunctions as mfun
import numpy as np
import struct

# -------------------------------------------------------
class MapFunctions:
    def __init__(self, pdb_code, mobj, pobj, interp):
        self.mobj = mobj
        self.pobj = pobj
        self.interp = interp
        self.pdb_code = pdb_code        
        self.mfunc = mfun.MapFunctions(
            self.pdb_code,self.mobj,self.pobj, interp)
        

# -------------------------------------------------------
class  MapFile:
    def __init__(self, pdb_code, ed_path):
        # PUBLIC INTERFACE        
        self.pdb_code = pdb_code       
        self.em_code = pdb_code  
        self.filepath_ccp4 = ed_path
        self.resolution = ""
        self.exp_method = ""
        self.map_header = {}
        self.header_as_string = ""        
        self.values = []                                
        self.F = -1 #fastest axis
        self.M = -1 #middle axis        
        self.S = -1 #slowest axis
        self.diff_has = 0        
        self.load_map()
        self.load_values()
# -------------------------------------------------------                   
    def load_map(self):
        try:
            with open(self.filepath_ccp4, mode='rb') as file:
                self._ccp4_binary = file.read()            
            self._create_mapheader(self._ccp4_binary)
            return True
        except Exception as e:
            print("Error loading map", str(e))
            return False
# -------------------------------------------------------
    def load_values(self):
        try:            
            self._create_mapvalues()
        except Exception as e:
            print(str(e))                
# -------------------------------------------------------
    def _create_mapheader(self, ccp4_binary):
        num_labels = 0
        num_sym = 0
        headers = [] #https://www.ccp4.ac.uk/html/maplib.html#description
        xheaders = []
        self.header_as_string = ""
        headers.append(["01_NC","int",4])           # of Columns    (fastest changing in map)
        headers.append(["02_NR","int",4])           # of Rows
        headers.append(["03_NS","int",4])           # of Sections   (slowest changing in map)
        headers.append(["04_MODE","int",4])         # Data type   0 = signed bytes (from-128 lowest to 127 highest) 1 = Integer*2 2 = Image stored as Reals 3 = Complex Integer*2 4 = Complex Reals 5 == 0
        headers.append(["05_NCSTART","int",4])      # Number of first COLUMN  in map
        headers.append(["06_NRSTART","int",4])      # Number of first ROW     in map
        headers.append(["07_NSSTART","int",4])      # Number of first SECTION in map
        headers.append(["08_NX","int",4])           # Number of intervals along X
        headers.append(["09_NY","int",4])           # Number of intervals along Y
        headers.append(["10_NZ","int",4])           # Number of intervals along Z
        headers.append(["11_X_length","double",4])  # Cell Dimensions (Angstroms)
        headers.append(["12_Y_length","double",4])  #             "
        headers.append(["13_Z_length","double",4])  #             "
        headers.append(["14_Alpha","double",4])     # Cell Angles     (Degrees)
        headers.append(["15_Beta","double",4])      #             "
        headers.append(["16_Gamma","double",4])     #             "
        headers.append(["17_MAPC","int",4])         # Which axis corresponds to Cols.  (1,2,3 for X,Y,Z)
        headers.append(["18_MAPR","int",4])         # Which axis corresponds to Rows   (1,2,3 for X,Y,Z)
        headers.append(["19_MAPS","int",4])         # Which axis corresponds to Sects. (1,2,3 for X,Y,Z)
        headers.append(["20_AMIN","double",4])      # Minimum density value
        headers.append(["21_AMAX","double",4])      # Maximum density value
        headers.append(["22_AMEAN","double",4])     # Mean    density value    (Average)
        headers.append(["23_ISPG","int",4])         # Space group number
        headers.append(["24_NSYMBT","int",4])       # Number of bytes used for storing symmetry operators
        headers.append(["25_LSKFLG","int",4])       # Flag for skew transformation, =0 none, =1 if foll
        for i in range(26,35):
            headers.append([str(i) + "_SKWMAT","double",4])       # Flag for skew transformation, =0 none, =1 if foll
        for i in range(35,38):
            headers.append([str(i) + "_SKWTRN","double",4])       # Flag for skew transformation, =0 none, =1 if foll
        for i in range(38,53):
            headers.append(["X","int",4])       # Flag for skew transformation, =0 none, =1 if foll
        headers.append(["53_MAP","string",4])       # Character string 'MAP ' to identify file type
        headers.append(["54_MACHST","int",4])       # Machine stamp indicating the machine type
        headers.append(["55_ARMS","double",4])       # Rms deviation of map from mean density
        headers.append(["56_NLABL","int",4])       # Number of labels being used

        i=0
        for header, typ,inc  in headers:
            val = ""
            if not header == "X":
                if typ == "int":
                    val = int.from_bytes(ccp4_binary[i:i+inc], byteorder='little', signed=True)
                    self.map_header[header] = val
                elif typ == "double":
                    val = struct.unpack('f', ccp4_binary[i:i+inc])[0]
                    self.map_header[header] = val
                elif typ == "string":
                    val = ccp4_binary[i:i+inc].decode("utf-8")
                    self.map_header[header] = val

                if len(header) > 7:
                    self.header_as_string += header + "\t" + str(val) + "\n"
                else:
                    self.header_as_string += header + "\t\t" + str(val) + "\n"

                if header == "24_NSYMBT":
                    num_sym = int(val/80)
                if header == "56_NLABL":
                    num_labels = int(val)

            i+=inc

        for s in range(0,num_labels):
            xheaders.append([str(s+1) + "_LABEL","string",80])       # 10  80 character text labels (ie. A4 format)
        for s in range(num_labels,10):
            xheaders.append(["X","string",80])       # 10  80 character text labels (ie. A4 format)
        for s in range(0,num_sym):
            xheaders.append([str(s+1) + "_SYM","string",80])       # 10  80 character text labels (ie. A4 format)


        for header, typ,inc  in xheaders:
            if not header == "X":
                if typ == "int":
                    val = int.from_bytes(ccp4_binary[i:i+inc], byteorder='little', signed=True)
                    self.map_header[header] = val
                elif typ == "double":
                    val = struct.unpack('f', ccp4_binary[i:i+inc])[0]
                    self.map_header[header] = val
                elif typ == "string":
                    val = ccp4_binary[i:i+inc].decode("utf-8")
                    self.map_header[header] = val

                if len(header) > 7:
                    self.header_as_string += header + "\t" + str(val) + "\n"
                else:
                    self.header_as_string += header + "\t\t" + str(val) + "\n"
            i+=inc
# -------------------------------------------------------    
    def _create_mapvalues(self):
        use_binary = self._ccp4_binary
        vals = []                
        Blength = self.map_header["01_NC"] * self.map_header["02_NR"] * self.map_header["03_NS"]
        Bstart = len(self._ccp4_binary) - (4 * Blength)

        self.F = self.map_header["01_NC"]
        self.M = self.map_header["02_NR"]
        self.S = self.map_header["03_NS"]        
        self.values = np.zeros((self.F,self.M,self.S))

        count = 0
        for s in range(0,self.S): #slow
            for m in range(0,self.M):#medium
                for f in range(0,self.F):#fast
                    strt = Bstart+(count*4)
                    val = struct.unpack('f', use_binary[strt:strt+4])[0]
                    count += 1                                        
                    self.values[f,m,s] = val
    
            
        

    


    
                           