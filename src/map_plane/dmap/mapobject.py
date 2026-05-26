"""
RSA 4/2/23
https://pynative.com/make-python-class-json-serializable/#:~:text=Use%20toJSON()%20Method%20to%20make%20class%20JSON%20serializable&text=So%20we%20don't%20need,Python%20Object%20to%20JSON%20string.

"""


class  MapObject(object):
    def __init__(self, pdb_code):
        # PUBLIC INTERFACE        
        self.pdb_code = pdb_code       
        self.em_code = pdb_code
        self.em_link = ""
        self.resolution = ""
        self.exp_method = ""
        self.map_header = {}
        self.header_as_string = ""        
        self.values = []
        #self.npy_values = []
        self.diff_values = [] 
        self.diff_has = 0
        #self.npy_diff_values = []
        self.F = -1 #fastest axis
        self.M = -1 #middle axis        
        self.S = -1 #slowest axis
           
        #self.values = {} #possible alternative if there are many 0s but it is much slower for high res xray data eg 4rek
        #self.diff_values = {}
        self.ebi_link = f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb_code}"
        self.em_link = f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb_code}" #if an electron microscopy may be a different link later
        self.ccp4_link = f"https://www.ebi.ac.uk/pdbe/entry-files/{self.pdb_code}.ccp4"
        self.diff_link = f"https://www.ebi.ac.uk/pdbe/entry-files/{self.pdb_code}_diff.ccp4"
        self.pdb_link = ""

    
    