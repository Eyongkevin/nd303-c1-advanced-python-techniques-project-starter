from models import OrbitPath, NearEarthObject
#from models import OrbitPath, NearEarthObject
import csv  # Library to read csv files


class NEODatabase(object):
    """
    Object to hold Near Earth Objects and their orbits.

    To support optimized date searching, a dict mapping of all orbit date paths to the Near Earth Objects
    recorded on a given day is maintained. Additionally, all unique instances of a Near Earth Object
    are contained in a dict mapping the Near Earth Object name to the NearEarthObject instance.
    """

    def __init__(self, filename):
        """
        :param filename: str representing the pathway of the filename containing the Near Earth Object data
        """
        # TODO: What data structures will be needed to store the NearEarthObjects and OrbitPaths?
        # TODO: Add relevant instance variables for this.

        self.filename = filename
        self.NearEarthObjects = dict()
        self.OrbitPaths = dict()

    @staticmethod
    def to_bool(str_bool):
        if str_bool == 'False':
            return False
        elif str_bool == 'True':
            return True
        else:
            return None

    def load_data(self, filename=None):
        """
        Loads data from a .csv file, instantiating Near Earth Objects and their OrbitPaths by:
           - Storing a dict of orbit date to list of NearEarthObject instances
           - Storing a dict of the Near Earth Object name to the single instance of NearEarthObject

        :param filename:
        :return:
        """

        if not (filename or self.filename):
            raise Exception('Cannot load data, no filename provided')

        filename = filename or self.filename
        # TODO: Check if it is a file and if it has the extension `csv`

        # TODO: Load data from csv file.
        with open(filename) as open_file:
            # TODO: Determine the exception here if fail to read file and handle it with a 'try: except: except'
            datas = csv.DictReader(open_file, delimiter=",")
            datas = list(datas)

            # TODO: Where will the data be stored?
            
            
            for data in datas:
                neoObj = NearEarthObject(neo_reference_id=data['id'],
                                                      name=data['name'],
                                                      diameter = float(data['estimated_diameter_min_kilometers']),
                                                      is_hazardous = NEODatabase.to_bool(data['is_potentially_hazardous_asteroid']
                                                     ))
                
                orbitPath = OrbitPath(name = data['name'],
                                      miss_distance_km = float(data['miss_distance_kilometers']), 
                                      orbit_date = data['close_approach_date'])
                
                # - Storing a dict of the Near Earth Object name to the single instance of NearEarthObject
                idx_name = data['name']
                if not idx_name in self.OrbitPaths:
                    self.OrbitPaths[idx_name] = neoObj
                    neoObj.update_orbits(orbitPath)
                    
                # - Storing a dict of orbit date to list of NearEarthObject instances   
                idx_date = data['close_approach_date']
                if idx_date in self.NearEarthObjects:
                    self.NearEarthObjects[idx_date] += [neoObj]
                else:
                    self.NearEarthObjects[idx_date] = [neoObj]


        return None