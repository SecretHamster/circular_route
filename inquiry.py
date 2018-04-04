# from config import Config
import urllib.request
from xml.dom import minidom
from xml.dom import Node
from job import Job

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class Inquiry:
    """
    This is a check to grab information from the FSEconomy servers to get information from a server
    """
    def __init__(self, config, direction, icao=None):
        """
        :param config: a config class object
        :param icao: the 4 letter code for the queried airport
        :param direction: to or from as a boolean (True = from, False = to)
        """
        self.config = config
        if icao == None:
            self.icao = self.config.get_icao()
        else:
            self.icao = icao
        self.direction = direction

    def go(self):
        """
        This gets a query for one single airport and dumps it into a dictionary and returns it
        :config: a config class with all the relevant default info
        :return: a dictionary of the Jobs
        """
        # for the test we will do the inquiry then just return the data
        direction = 'jobsfrom'
        if self.direction:
            direction = 'jobsto'

        base_get = "{}data?userkey={}&format=xml&query=icao&search={}&icaos={}".format(self.config.get_url(),
                                                                                       self.config.get_access_key(),
                                                                                       direction,
                                                                                       self.icao)
        # print(base_get)
        root = minidom.parseString(urllib.request.urlopen(base_get).read())

        # we need to check if we get an error
        errors = root.getElementsByTagName('Error')
        for error in errors:
            raise PermissionError(getText(error.childNodes))

        # so we want all the Assignment elements
        assignments = root.getElementsByTagName('Assignment')
        # children = len(assignments)

        # print("Found {} Assignments:".format(children))

        # and we store them in a dictionary to pass back to the calling function
        return_list = dict()

        for assignment in assignments:
            # we go through each of the child nodes (the Assignment parameters) and drop them into a dictionary
            # after that we create a job using the parameters and drop that into the dictionary above
            node_dict = dict()
            for child in assignment.childNodes:
                if child.nodeType == Node.ELEMENT_NODE:
                    node_name = child.nodeName
                    element_id = assignment.getElementsByTagName(child.nodeName)[0]
                    node_value = getText(element_id.childNodes)
                    node_dict[node_name] = node_value
            new_job = Job(node_dict['Id'], node_dict['Location'], node_dict['ToIcao'], node_dict['FromIcao'],
                          node_dict['Amount'], node_dict['UnitType'], node_dict['Commodity'], node_dict['Pay'],
                          node_dict['ExpireDateTime'], node_dict['PtAssignment'], node_dict['Type'],
                          node_dict['AircraftId'])
            return_list[new_job.get_id()] = new_job

        # and finally return the list of jobs back to the calling function
        return return_list
