from enum import Enum
import csv
from exceptions import DataHasIncorrectAttributesError, FormatHasINvalidValueError

import logging

logging.basicConfig(level=logging.DEBUG,
                    filename='ex1Log.txt',
                    format=' %(asctime)s - %(levelname)s - %(message)s' )

logging.debug('START DEBUG')

class OutputFormat(Enum):
    """
    Enum representing supported output formatting options for search results.
    """
    display = 'display'
    csv_file = 'csv_file'

    @staticmethod
    def list():
        """
        :return: list of string representations of OutputFormat enums
        """
        return list(map(lambda output: output.value, OutputFormat))


class NEOWriter(object):
    """
    Python object use to write the results from supported output formatting options.
    """

    def __init__(self):
        # TODO: How can we use the OutputFormat in the NEOWriter?
        self.output_format = OutputFormat.list()
        self.neo_fields = ['id','name','orbits','orbit_dates']
        self.orbitPath_fields = ['name','miss_distance_km','orbit_date']

    def format_matrix(self, header, matrix,
                    top_format, left_format, cell_format, row_delim, col_delim):
        
        table = [[''] + header] + [[""] + row for row in matrix]
        table_format = [['{:^{}}'] + len(header) * [top_format]] \
                    + len(matrix) * [[left_format] + len(header) * [cell_format]]
             
        col_widths = [max(
                        len(format.format(cell, 0))
                        for format, cell in zip(col_format, col))
                    for col_format, col in zip(zip(*table_format), zip(*table))]
        return row_delim.join(
                col_delim.join(
                    format.format(cell, width)
                    for format, cell, width in zip(row_format, row, col_widths))
                for row_format, row in zip(table_format, table))

    def write(self, format, data, **kwargs):
        """
        Generic write interface that, depending on the OutputFormat selected calls the
        appropriate instance write function

        :param format: str representing the OutputFormat
        :param data: collection of NearEarthObject or OrbitPath results
        :param kwargs: Additional attributes used for formatting output e.g. filename
        :return: bool representing if write successful or not
        """
        # TODO: Using the OutputFormat, how can we organize our 'write' logic for output to stdout vs to csvfile
        # TODO: into instance methods for NEOWriter? Write instance methods that write() can call to do the necessary
        # TODO: output format.

        # For Command line display, display in tables and Format date in human readable format. 

        if format == self.output_format[0]:
            print("Writing to Command Line....\n")
            #logging.debug(str(dir(data[0])))
            if hasattr(data[0], 'neo_name'):
                print("Printing {} Orbit paths from search...\n".format(len(data)))
                headers = ['Name', 'Miss Distance Km', 'Orbit Date']
                result = []
                for orbit in data:
                    result.append([orbit.neo_name, orbit.miss_distance_kilometers, orbit.close_approach_date])

                
            elif hasattr(data[0], 'name'):
                #logging.debug(str(dir(data[0])))
                headers = ['ID','Name','Orbits','Orbit Dates']
                result = []
                for neo in data:
                    orbit = [orbit.neo_name for orbit in neo.orbits]
                    orbit=','.join(orbit)
                    orbit_dates = [orbit.close_approach_date for orbit in neo.orbits]
                    orbit_dates = ','.join(orbit_dates)
                    result.append([neo.id, neo.name, orbit, orbit_dates])

            else:
                raise DataHasIncorrectAttributesError("Data doesn't have attributes `name` or `neo_name`")

            print(self.format_matrix(headers,
                    result,
                    '{:^{}}', '{:>{}}', '{:>{}}', '\n', ' | '))
                                

            """ try:
                print(data)
            except IOError as ex:
                print("Error printing") """
        elif format == self.output_format[1]:
            print("Writing to CSV file....")
            with open('data/output/results.csv', 'w', newline='') as neo_results:

                # NEO Object
                if hasattr(data[0], 'neo_name'):
                    print("Orbit")
                    try:
                        writer = csv.DictWriter(neo_results, fieldnames=self.orbitPath_fields)
                        writer.writeheader()

                        for orbit_obj in data:
                            writer.writerow({                           
                                'name':orbit_obj.neo_name,
                                'miss_distance_km':orbit_obj.miss_distance_kilometers,
                                'orbit_date': orbit_obj.close_approach_date

                            })

                        return True
                    except IOError as ioe:
                        print("Error:", ioe)
                        return False


                elif hasattr(data[0], 'name'):
                    print("NEO")
                    try:
                        writer = csv.DictWriter(neo_results, fieldnames=self.neo_fields)
                        writer.writeheader()

                        for neo_obj in data:
                            writer.writerow({
                                'id':neo_obj.id,
                                'name':neo_obj.name,
                                'orbits':[orbit.neo_name for orbit in neo_obj.orbits],
                                'orbit_dates': [orbit.close_approach_date for orbit in neo_obj.orbits]

                            })
                        return True
                    except IOError as ioe:
                        print("Error:", ioe)
                        return False
        else:
            raise FormatHasINvalidValueError("`format` should be either `csv_file` or `display` ")



