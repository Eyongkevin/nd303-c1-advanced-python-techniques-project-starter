from collections import namedtuple, defaultdict
from enum import Enum
import random
import operator

from exceptions import UnsupportedFeature,ArgDatesInputChoiceError
from models import NearEarthObject, OrbitPath

import logging

logging.basicConfig(level=logging.DEBUG,
                    filename='ex1Log.txt',
                    format=' %(asctime)s - %(levelname)s - %(message)s' )

#logging.disable(logging.CRITICAL)
logging.debug('START DEBUG')



class DateSearch(Enum):
    """
    Enum representing supported date search on Near Earth Objects.
    """
    between = 'between'
    equals = 'equals'

    @staticmethod
    def list():
        """
        :return: list of string representations of DateSearchType enums
        """
        return list(map(lambda output: output.value, DateSearch))


class Query(object):
    """
    Object representing the desired search query operation to build. The Query uses the Selectors
    to structure the query information into a format the NEOSearcher can use for date search.
    """

    Selectors = namedtuple('Selectors', ['date_search', 'number', 'filters', 'return_object'])
    DateSearch = namedtuple('DateSearch', ['type', 'values'])
    ReturnObjects = {'NEO': NearEarthObject, 'Path': OrbitPath}

    def __init__(self, **kwargs):
        """
        :param kwargs: dict of search query parameters to determine which SearchOperation query to use
        """
        # TODO: What instance variables will be useful for storing on the Query object?
        self.number = kwargs['number']
        self.date = kwargs.get('date', None) 
        self.start_date = kwargs.get('start_date', None) 
        self.end_date = kwargs.get('end_date', None)  
        self.filters = kwargs.get('filter', None)
        self.return_object = kwargs['return_object']


    def build_query(self):
        """
        Transforms the provided query options, set upon initialization, into a set of Selectors that the NEOSearcher
        can use to perform the appropriate search functionality

        :return: QueryBuild.Selectors namedtuple that translates the dict of query options into a SearchOperation
        """

        # TODO: Translate the query parameters into a QueryBuild.Selectors object
        if (self.date and (not self.start_date and not self.end_date )):
            date_search = Query.DateSearch('equals',self.date)
        
        elif (self.start_date and self.end_date and not self.date):
            date_search = Query.DateSearch('between',[self.start_date, self.end_date])
        else:
            raise ArgDatesInputChoiceError("Either --date should be given or both --start_date and --end_date are given")

        selector = Query.Selectors(date_search, self.number, self.filters, Query.ReturnObjects[self.return_object])
        return selector


class Filter(object):
    """
    Object representing optional filter options to be used in the date search for Near Earth Objects.
    Each filter is one of Filter.Operators provided with a field to filter on a value.
    """
    Options = {
        # TODO: Create a dict of filter name to the NearEarthObject or OrbitalPath property
        'diameter': 'diameter_min_km',
        'is_hazardous' : 'is_potentially_hazardous_asteroid',
        'distance':'miss_distance_kilometers'
    }

    Operators = {
        # TODO: Create a dict of operator symbol to an Operators method, see README Task 3 for hint
        '=' : operator.eq,
        '>' : operator.gt,
        '>=' : operator.ge
    }

    def __init__(self, field, object, operation, value):
        """
        :param field:  str representing field to filter on
        :param field:  str representing object to filter on
        :param operation: str representing filter operation to perform
        :param value: str representing value to filter for
        """
        self.field = field
        self.object = object
        self.operation = operation

        if value == 'True':
                self.value = True
        elif value == 'False':
            self.value = False
        else:
            self.value = float(value)

    @staticmethod
    def create_filter_options(filter_options):
        """
        Class function that transforms filter options raw input into filters

        :param input: list in format ["filter_option:operation:value_of_option", ...]
        :return: defaultdict with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        """

        # TODO: return a defaultdict of filters with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        filter_option_dic = defaultdict(lambda: [])
        for filter_option in filter_options:    
            field, operation, value = filter_option.split(':')
            for key, obj in Query.ReturnObjects.items():
                if field in list(obj.__dict__.keys()):    
                    filter_obj = Filter(field, key, operation, value)
                    filter_option_dic[key] = filter_option_dic[key] + [filter_obj] 
                    break
            
        return filter_option_dic


    def apply(self, results):
        
        """
        Function that applies the filter operation onto a set of results

        :param results: List of Near Earth Object results
        :return: filtered list of Near Earth Object results
        """
        # TODO: Takes a list of NearEarthObjects and applies the value of its filter operation to the results
        if self.object == 'NEO':
            
            return list(filter(
                lambda neo: Filter.Operators[self.operation](getattr(neo, Filter.Options[self.field]), 
                                                             self.value ), results
                )
            )
        elif self.object == 'Path':
          
            unique_orbits = {}

            for orbit in results:
                date_name = f'{orbit.close_approach_date}.{orbit.neo_name}'
                if date_name not in unique_orbits:
                    if Filter.Operators[self.operation](
                        getattr(orbit, Filter.Options[self.field]), self.value):
                        unique_orbits[date_name] = orbit
               
            
            return list(unique_orbits.values())


class NEOSearcher(object):
    """
    Object with date search functionality on Near Earth Objects exposed by a generic
    search interface get_objects, which, based on the query specifications, determines
    how to perform the search.
    """
    orbit_properties = ['distance']

    def __init__(self, db):
        """
        :param db: NEODatabase holding the NearEarthObject instances and their OrbitPath instances
        """
        self.db = db
        # TODO: What kind of an instance variable can we use to connect DateSearch to how we do search?

    def search_equals(self, date, return_obj):
        neo_dates = self.db.NearEarthObjects[date]
        unique_neo = {}
        
        for neo_date in neo_dates:
            neo_name = neo_date.name
            if not neo_name in unique_neo:
                unique_neo[neo_name] = neo_date
  
        return list(unique_neo.values())

       
    def search_between(self,start_date, end_date,return_obj):
        filtered_neo = {key:value for (key,value) in self.db.NearEarthObjects.items() if key >= start_date and key <= end_date}
        shuf_keys = list(filtered_neo.keys())
        #random.shuffle(shuf_keys)

        unique_neo = {}

        for date_key in shuf_keys:
            for data in filtered_neo[date_key]:
                neo_name = data.name
                if not neo_name in unique_neo:
                    unique_neo[neo_name] = data
      
            
        return list(unique_neo.values())
        
    def filter_objects(self, filters, results):
        # Apply filter if not None
        filter_obj = Filter.create_filter_options(filters)
        for key, objs in filter_obj.items():
            for obj in objs:
                results = obj.apply(results)
            
        return results

    def return_orbits_in_neo(self, neos):
        all_orbits = []

        for neo in neos:
            all_orbits += neo.orbits
        return all_orbits

    def return_neo_from_orbits(self, orbits):
        return [self.db.OrbitPaths[orbit.neo_name] for orbit in orbits ]    
        

    def get_objects(self, query):
        """
        Generic search interface that, depending on the details in the QueryBuilder (query) calls the
        appropriate instance search function, then applys any filters, with distance as the last filter.

        Once any filters provided are applied, return the number of requested objects in the query.return_object
        specified.

        :param query: Query.Selectors object with query information
        :return: Dataset of NearEarthObjects or OrbitalPaths
        """
        # TODO: This is a generic method that will need to understand, using DateSearch, how to implement search
        # TODO: Write instance methods that get_objects can use to implement the two types of DateSearch your project
        # TODO: needs to support that then your filters can be applied to. Remember to return the number specified in
        # TODO: the Query.Selectors as well as in the return_type from Query.Selectors
        type_date = query.date_search.type

        number = query.number
        filters = query.filters
        return_obj = query.return_object
        if ((type_date in DateSearch.list()) and type_date == 'equals'):
            date = query.date_search.values
            results = self.search_equals(date, return_obj)
            
        elif((type_date in DateSearch.list()) and type_date == 'between'):
            start_date, end_date = query.date_search.values
            results =  self.search_between(start_date, end_date, return_obj)
            
        #logging.debug("Properties of one Object is "+ str(dir(results[0])))


        
        #assert return_obj == NearEarthObject, "This is not an Object"
        #logging.debug("Orbit fron neo is "+ str(dir(result_orbits[0])))

        orbit_filters = []
        # Apply filter if not None 
        if filters:
            
            filter_obj = Filter.create_filter_options(filters)
            for key, objs in filter_obj.items():
                for obj in objs:
                    #logging.debug(str(obj.field))
                    if obj.field in NEOSearcher.orbit_properties:
                        orbit_filters.append(obj)
                        continue
                    results = obj.apply(results)
        

        result_neo = results
        result_orbits = self.return_orbits_in_neo(result_neo)

        if orbit_filters:
            for orbit_filter in orbit_filters:
                result_orbits = orbit_filter.apply(result_orbits)

            result_neo = self.return_neo_from_orbits(result_orbits)

        
        if return_obj == NearEarthObject:
            return result_neo[:number]
        elif return_obj == OrbitPath:
            return result_orbits[:number]
        else:
            return None



        
        