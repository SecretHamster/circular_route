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

import argparse
import time
import logging

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler('circular_route.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.setLevel(logging.ERROR)
    logger.addHandler(fh)

    logger.log(60, "Starting logging")

    """
    We currently have one command line parameter
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", metavar="configuration filename", help="configuration file with default information",
                        required=True)
    parser.add_argument("-a", metavar="airport code", help="The four letter icao code for the airport")

    args = parser.parse_args()

    # assign the config from the file
    default_config = Config(args.c)

    path_found = False
    path_start = default_config.get_icao().upper()
    logger.debug("Default airport set to: {}".format(path_start))
    if args.a:
        path_start = str(args.a).upper()
        logger.debug("Resetting initial airport to {}".format(path_start))
    path_nodes = dict()
    metric = 1
    path_nodes[path_start] = Node(path_start)
    path_nodes[path_start].set_distance(0)
    inquiry_queue = [path_start]
    logger.debug(path_nodes[path_start])

    while not path_found and len(inquiry_queue) > 0:
        query = "-".join(inquiry_queue)

        logger.debug("Query airports are {}".format(query))
        test_inquiry = Inquiry(default_config, True, query)
        job_list = test_inquiry.go()

        for job, job_value in job_list.items():
            name = job_value.get_location()
            current_node = job_value.get_to_icao()
            logger.debug("Current node: {}, checking next node {}".format(name, current_node))
            if name not in path_nodes:
                path_nodes[name] = Node(name)
                inquiry_queue.append(name)
                logger.debug("Adding {}".format(name))
            if job_value.is_valid():
                logger.debug("Updating {}".format(name))
                path_nodes[name].set_next_hop(current_node, path_nodes[current_node].get_distance()+1)
                logger.debug(path_nodes[name])
                if name == path_start:
                    path_nodes[path_start].overwrite_next_hop(current_node)
                    path_nodes[path_start].set_distance(path_nodes[current_node].get_distance()+1)
                    path_found = True

        metric += 1
        # max 10 inquiries per minute
        time.sleep(6)

    logger.debug(path_nodes[path_start])

    logger.debug("Path found: {}".format(path_found))
    for node in path_nodes:
        logger.debug(path_nodes[node])

    path_found = False
    path = list()
    path.append(path_start)
    while not path_found:
        next_hop = path_nodes[path[-1]].get_next_hop()
        path.append(next_hop)
        if next_hop == path_start:
            path_found = True

    for node in path:
        print("{} -> ".format(node), end='')
        logger.info("{} -> ".format(node))

    fh.close()
