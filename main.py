#!/usr/bin/python3

"""
This program will find routes from FSEconomy server and try to find a circular route with various parameters. Rather
than having to figure out a rule manually.

Initially it will simple find the shortest circular hop. Later on we will introduce minimum sizes, payments and perhaps
even distances
"""

from config import Config
from inquiry import Inquiry
from path import Node
import treelib

import argparse
import time
# import logging
import logging.config
import os

import pickle

"""
We discover the current directory of this file and create the path for the logging configuration before opening it
"""
filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs/logging.conf")
logging.config.fileConfig(filename)


class Main:
    def __del__(self):
        """
        We are going to save the jobs files here and load them next time.
        Currently there will be no timeout, but we will add this later
        :return:
        """
        pass

    def __init__(self):
        self._logger = logging.getLogger('main')
        self._output = logging.getLogger('output')
        self._logger.log(60, "Starting logging")
        self.job_list = {}

        """
        We currently have one command line parameter
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", metavar="configuration filename", help="configuration file with default information",
                            required=True)
        parser.add_argument("-d", metavar="airport code", help="The four letter icao code for the [d]eparting airport")
        parser.add_argument("-a", metavar="airport code",
                            help="The four letter icao code for the destin[a]tion airport")

        args = parser.parse_args()

        # assign the config from the file
        self.default_config = Config(args.c)

        '''To start off with we have no path found and we set our destination point. If a end point isn't set on the
        command line, we take the default from the config file'''
        # TODO we should alter to use the config to contain all the variables, rather than directly from the command line
        self.path_found = False
        self.path_start = self.default_config.get_icao().upper().strip()
        self.path_finish = self.default_config.get_icao_destination().upper().strip()
        self._logger.debug("Default departing node set to: {}".format(self.path_start))
        self._logger.debug("Default destination node set to: {}".format(self.path_finish))
        if args.a:
            self.path_finish = str(args.a).upper().strip()
            self._logger.debug("Resetting destination airport to {}".format(self.path_finish))
        if args.d:
            self.path_start = str(args.d).upper().strip()
            self._logger.debug("Resetting departing airport to {}".format(self.path_start))

        '''We create a container for the nodes we've checked and set the metric to indicate the first hop
        Add the starting point to the container as this is the first one we check, and set it's distance to 0
        We do an initial inquiry using the start point'''
        # path_nodes uses the icao code as the key
        self.path_nodes = dict()
        self.metric = 0
        # TODO this could cause us problems if path_start == path_end. This is a valid thing
        # we don't need the start in, we're not tracing from there
        self.path_nodes[self.path_finish] = Node(self.path_finish, is_destination=True)
        self.path_nodes[self.path_start] = Node(self.path_start, is_departure=True)
        self._logger.debug(self.path_nodes[self.path_finish])

    def go(self):
        """Until we get the a successful path resolution then we keep going round our route trying to find a solution
        we create the query object by adding on all the elements of the inquiry queue
        """
        inquiry_queue = [self.path_finish]
        path_found = False

        while not path_found and len(inquiry_queue) > 0:
            self._logger.debug("Path not found and query length > 0")
            query = "-".join(inquiry_queue)

            self._logger.debug("Query airports are {}".format(query))
            test_inquiry = Inquiry(self.default_config, True, query)

            # self._logger.debug(f"Clearing queue of size {len(inquiry_queue)}")
            # inquiry_queue.clear()
            # we are now one step on
            self.metric += 1
            try:
                current_job_list = test_inquiry.go()
            except PermissionError as e:
                self._logger.critical("Permission not granted, please check url {} and key {}".format(
                    self.default_config.get_url(), self.default_config.get_access_key()))
                exit(-1)

            path_found, inquiry_queue = self.iterate_job_list(current_job_list)

            # max 10 inquiries per minute
            time.sleep(6)

        self._output.info(f"Searching for optimal path")

        self._logger.debug("Path found: {}".format(self.path_found))

        if self._logger.level == logging.DEBUG:
            for node in self.path_nodes:
                self._logger.debug(self.path_nodes[node])

        self._logger.debug(f"Size of jobs list is {len(self.job_list)} keys listed below\nkeys {self.job_list.keys()}")

        self.print_nested_job_list(self.find_route().paths_to_leaves(), self.find_route())

    def iterate_job_list(self, current_job_list):
        inquiry_queue = []
        path_found = False
        """
        Once we have the inquiry queue results we iterate through the list
                    link the current node to a new previous node
                    if is a new node we add it into the list of nodes we have queried already
                    if the job is valid we also then also add it to it's path node list
                    Finally if the new node is the start node, we've found a solution
                    Otherwise we add one to the hop metric and start again
                    """
        for job, job_value in current_job_list.items():
            self._logger.debug("next job in list")
            name = job_value.get_to_icao()              # This is the node we have just queried
            previous_node = job_value.get_from_icao()   # This is the node that the job is from
            self._logger.debug("Current node: {}, checking previous node {}".format(name, previous_node))
            if job_value.is_valid():
                # add job to our global collection so we can find the details later
                self._logger.debug(f"Adding job {job}")
                self.job_list[job] = job_value
                if previous_node not in self.path_nodes:
                    self.path_nodes[previous_node] = Node(previous_node)
                    # TODO we should look in our pickle list to see if the values are there, and take if untimed out
                    # testing out if nodes only need to be in if not already in, this seems logical
                    inquiry_queue.append(previous_node)
                    self._logger.debug(f"Adding {previous_node} to the inquiry queue")
                self._logger.debug("Updating {}".format(previous_node))
                # The new node add the metric
                self.path_nodes[previous_node].add_previous_hop(job_value.get_id(),
                                                                self.path_nodes[name].find_lowest_metric()+1)
                self._logger.debug(self.path_nodes[previous_node])
                if name == self.path_finish:
                    self.path_nodes[previous_node].set_next_hop_finish()
                if previous_node == self.path_start:
                    path_found = True
                    self.path_nodes[name].set_previous_hop_start()
                self._logger.debug(f"Current size of inquiry queue = {len(inquiry_queue)}")
        return path_found, inquiry_queue

    def find_route(self):
        """
        This finds the route from the known list of jobs, starting with the departing node
        Currently returns nothing, but we need better output so people can understand the route
        :return: A dictionary of job hops
        """
        self._output.info("Route Found\nNow looking for the path")
        # create the treelib for the pathing, add the starting node to it
        routes = treelib.Tree()
        routes.create_node(self.path_start, self.path_start)

        # path list contains the hops (the jobs) that stretch back to the beginning, we don't care about the nodes
        path_list = list()

        # load up the initial list with the 1st hop's shortest routes
        path_list.append(self.path_start)

        """
        So now we go to the start and work our way forwards. There should only be valid routes as long as we find 
        the shortest metric out each time
        """

        self.path_add(path_list, routes)

        if routes.depth() > 1:
            # we have a route
            self._output.info(routes.show())
        else:
            # no routes found out
            self._output.info("No route could be found")
        return routes

    def path_add(self, list_of_paths, tree_route):
        self._logger.debug("Searching for the path")
        path_found = False

        while not path_found:
            if len(list_of_paths) > 0:
                self._logger.debug(f"Current list of paths to find routes from {list_of_paths}")
                current_tree_node = tree_route.get_node(list_of_paths.pop(0))  # gets the node of the front of the path

                # the root is a icao node not a job
                if current_tree_node.is_root():
                    # we know these jobs will be unique so can safely add them without fear
                    for path in self.path_nodes[current_tree_node.tag].shortest_routes():
                        job_id = path[0]
                        self._logger.debug(f"Adding the node {job_id} to tree and new_short_paths")
                        tree_route.create_node(job_id, job_id, parent=self.path_start)
                        list_of_paths.append(job_id)
                # otherwise we go down the conventional route of find jobs and adding them to the next list
                else:
                    current_job = current_tree_node.identifier                          # id of the new job
                    current_node = self.job_list[current_tree_node.tag].get_to_icao()   # the icao the new job hops to
                    new_short_paths = self.path_nodes[current_node].shortest_routes()   # the links out of that icao

                    # for each path we find, we look at the first in the list, which is the closest to the end
                    self._logger.debug(f"icao for {current_node}")
                    """
                    we then retrieve the job referring to the job in the path and the tree node from thatwe then look at
                    the next hop in the list and so forth
                    We need to add the next node in the list, if it does not already exist and add this route to its
                    list
                    """
                    self._logger.debug(f"Links from node {current_node} is/are {new_short_paths}")
                    # when we get back multiple rules
                    if len(new_short_paths) > 0:
                        # first_path = True
                        for paths in new_short_paths:
                            self._logger.debug(f"Multiple new path found {paths[0]}")
                            itr = 0
                            job_identifier = f"{paths[0]}_{itr}"
                            # make sure we have a unique id for this hop
                            while job_identifier in tree_route:
                                itr += 1
                                job_identifier = f"{paths[0]}_{itr}"
                            self._logger.debug(f"New identifier is {job_identifier}")
                            list_of_paths.append(job_identifier)    # add new jobs to path query list
                            tree_route.create_node(paths[0], job_identifier, parent=current_job) # insert into tree
                            # and test for final hop
                            if self.job_list[paths[0]].get_to_icao() == self.path_finish:
                                self._logger.debug("We have got to the end")
                                path_found = True
                                self._output.info(f"To Destination {self.path_finish}")
                    else:
                        self._logger.debug(f"Single new path found {self.job_list[new_short_paths[0][0]]}")
                        itr = 0
                        job_identifier = f"{paths[0][0]}_{itr}"
                        # make sure we have a unique id for this hop
                        while job_identifier in tree_route:
                            itr += 1
                            job_identifier = f"{paths[0][0]}_{itr}"
                        list_of_paths.append(job_identifier)
                        tree_route.create_node(paths[0][0], job_identifier, parent=current_job.id)
                        # and test for final hop
                        if self.job_list[new_short_paths[0][0]].get_to_icao() == self.path_finish:
                            self._logger.debug("We have got to the end")
                            path_found = True
                            self._output.info(f"To Destination {self.path_finish}")
            else:
                self._logger.error("Tried to path an empty list in path_add")
                raise ValueError("path_add new_short_path is empty")

        return tree_route

    def print_nested_job_list(self, a, tree_route):
        """
        This prints out a group of nested jobs
        :return: None
        """

        for x in a:
            if isinstance(x, list):
                self.print_nested_job_list(x, tree_route)
            else:
                try:
                    print(self.job_list[tree_route.get_node(x).tag])
                except KeyError:
                    print(x)


if __name__ == '__main__':
    main = Main()
    main.go()
