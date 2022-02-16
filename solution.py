from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import List
from argparse import ArgumentParser
import csv
import copy
import sys
import json

"""
Some notes on terminology:
*flight: Direct flight connection between two cities
*route: One way trip from origin to destination/ origin to middle destination/
        middle destination to destination/destination to origin
*path: Full trip which differs from route in case of return or multicity
"""

def parse_arguments():
    """ Parse input arguments"""

    parser = ArgumentParser()

    parser.add_argument('dataset', type=str, help='Path to flight dataset in a csv file')
    parser.add_argument('origin', type=str, help='Origin airport code')
    parser.add_argument('destination', type=str, help='Destination airport code')
    parser.add_argument('--bags', type=int, help='Number of requested bags', default=0)
    parser.add_argument('--return', action='store_true', help='Is it a return flight?', dest='is_return')
    parser.add_argument('--days_of_stay', type=int, help=('In case of return trip, minimum days of stay at destination. '
                                                          'In case of multicity trip, minimum days of stay at mid stop.'), default=0)
    parser.add_argument('--max_layover_hours', type=int, help='Maximum layover hours between flights.', default=6)
    parser.add_argument('--max_travel_hours', type=int, help=('Maximum travel hours in a route. '
                                                              '0 for no restrictions.'), default=0)
    parser.add_argument('--max_nr_changes', type=int, help=('Maximum number of changes in a route. '
                                                            '0 for direct flights only, -1 for no restrictions.'), default=-1)
    parser.add_argument('--day_of_departure', type=str, help='String of departure with format %Y-%m-%d', default='')
    parser.add_argument('--multicity', action='store_true', help='Is multicity flight?', dest='is_multicity')
    parser.add_argument('--middle_destination', type=str, help=('Middle destination ariport code '
                                                              'in case of multicity trip'), dest='mid_dst', default='')

    input_arguments = parser.parse_args(sys.argv[1:])

    return [input_arguments.dataset, input_arguments.origin,
            input_arguments.destination, input_arguments.bags,
            input_arguments.is_return, input_arguments.days_of_stay,
            input_arguments.max_layover_hours, input_arguments.max_travel_hours,
            input_arguments.max_nr_changes, input_arguments.day_of_departure,
            input_arguments.is_multicity, input_arguments.mid_dst]

def generateAdjacencyDict(edges, header):
    """
    Describe: Generates dictionary with origins as keys and flights from the origins as values.
    Input: edges: List of flights that are represented in list with its attributes
           header: List of attribute names of flights
    Output: adjacencyDict: Dictionary with origins as keys and flights from the origins as values
    """
    adjacencyDict = defaultdict(list)
    index_of_origin = header.index("origin")

    for flight in edges:
        adjacencyDict[flight[index_of_origin]].append(dict(zip(header, flight)))

    return adjacencyDict

def addPath(path, journeys):
    """
    Describe: Drops first element of each route (list) within 'path' list
    Input: path: List of routes (list) containing flights (dict)
           journeys: List of paths (list)
    Output: journeys: List of paths (list) with new path ('final_path') added
    """
    final_path = []

    for route in path:
        route.pop(0)
        final_path.append(route)

    journeys.append(final_path)

    return journeys

def isNotVisited(x, path):
    """
    Describe: Check if new flight's destination 'x' is already present in last element of 'path' list
    Input: x : String of destination of flight to be appended
           path: List of routes (list) containing flights (dict)
    Output: 1 if not present, 0 if present
    """
    size = len(path[-1])
    for i in range(size):
        if (path[-1][i]["destination"] == x):
            return 0

    return 1

def isLayoverCompatible(x, path, max_layover_hours = 6):
    """
    Describe: Checks if layover time between new flight's departure 'x' and the last arrival of last element of
              'path' list does not exceed max_layover_hours
    Input: x: String of departure with format "%Y-%m-%dT%H:%M:%S" of flight to be appended
           path: List of routes (list) containing flights (dict)
           max_layover_hours: Integer, maximum time (hours) difference between two consecutive flights
    Output: 1 if does not exceed, 0 if exceeds
    """
    try:
        path[-1][-1]["arrival"]
    except KeyError:
        return 1

    if ((datetime.strptime(x, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(path[-1][-1]["arrival"], "%Y-%m-%dT%H:%M:%S"))
        >=timedelta(hours=1)) & \
        ((datetime.strptime(x, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(path[-1][-1]["arrival"], "%Y-%m-%dT%H:%M:%S"))
        <=timedelta(hours=max_layover_hours)):
        return 1

    return 0

def isStayLengthCompatible(x, path, days_of_stay = 0):
    """
    Describe: Check if time difference between new flight's departure 'x' and the last arrival of first element of
              'path' list exceeds days_of_stay
    Input: x: String of departure with format "%Y-%m-%dT%H:%M:%S" of flight to be appended
           path: List of routes (list) containing flights (dict)
           days_of_stay: Integer, minimum time (days) difference between two flights that are not in the same route
    Output: 1 if time difference is greater or equal to the days_of_stay, 0 otherwise
    """
    if len(path)==1:
        return 1
    elif ((datetime.strptime(x, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(path[0][-1]["arrival"], "%Y-%m-%dT%H:%M:%S"))
        >=timedelta(days=days_of_stay)):
        return 1
    return 0

def isTravelTimeCompatible(x, path, max_travel_hours=0):
    """
    Describe: Check if time difference between new flight's 'x' arrival and the first departure of the last element of
              'path' list exceeds max_travel_hours
    Input: x: Flight to be appended
           path: List of routes (list) containing flights (dict)
           max_travel_hours: Integer, maximum time (hours) difference between first and last flights in the same route
    Output: 1 if time difference does not exceed max_travel_hours, 0 otherwise
    """
    if max_travel_hours==0:
        return 1 
    elif len(path[-1])==1:
        if ((datetime.strptime(x["arrival"], "%Y-%m-%dT%H:%M:%S") - datetime.strptime(x["departure"], "%Y-%m-%dT%H:%M:%S"))
            <=timedelta(hours=max_travel_hours)):
            return 1
        else:
            return 0
    elif ((datetime.strptime(x["arrival"], "%Y-%m-%dT%H:%M:%S") -
    datetime.strptime(path[-1][1]["departure"], "%Y-%m-%dT%H:%M:%S"))
        <=timedelta(hours=max_travel_hours)):
        return 1
    return 0

def isNrChangesCompatible(path, max_nr_changes=0):
    """
    Describe: Check if adding another flight into a route does not exceed max_nr_changes
    Input: path: List of routes (list) containing flights (dict)
           max_nr_changes: Integer, maximum number of changes in a route. 0 indicates direct flight, -1 indicates no restriction.
    Output: 1 if adding new flight does not exceed maximum number of changes, 0 otherwise
    """
    if len(path[-1])==1:
        return 1
    elif (max_nr_changes==-1) | (len(path)<max_nr_changes+1):
        return 1
    return 0

def isDepartureDateCompatible(x, path, day_of_departure):
    """
    Describe: Check if new flight's departure 'x' is on the 'day_of_departure' and if it is the first flight in the first outbound route
    Input: x: String of departure with format "%Y-%m-%dT%H:%M:%S" of flight to be appended
           path: List of routes (list) containing flights (dict)
           day_of_departure: String of departure with format "%Y-%m-%d", "" if no departure day defined
    Output: 1 if new flight is not the first flight in the first outbound route or
            if new flight's departure is on the 'day_of_departure', else 0
    """
    if day_of_departure =="":
        return 1
    elif (len(path[0])==1) & (datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").date()
                              != datetime.strptime(day_of_departure, "%Y-%m-%d").date()):
        return 0
    return 1

def isMultiCityCompatible(x, path, is_multicity, src, dst):
    """
    Describe: When is_multicity==True, check if new flight's destination 'x' is not the final destination
              when it is in the first outbound route and if new flight's destination 'x' is not the source airport
              when it is in the second outbound route. i.e. when user wants to travel multicity
              Budapest -> London -> Barcelona we do not want to output routes like
              Budapest -> Barcelona -> London -> Barcelona and
              Budapest -> Barcelona -> Budapest -> London
    Input: x: String of destination of flight to be appended
           path: List of routes (list) containing flights (dict)
           is_multicity: True / False
           src: String, source airport
           dst: String, final destination airport
    Output: 1 if meets above criteria, 0 otherwise
    """
    if (is_multicity==True) & (len(path)==1) & (x != dst):
        return 1
    elif (is_multicity==True) & (len(path)==2) & (x != src):
        return 1
    elif is_multicity==False:
        return 1
    return 0

def isBagCompatible(x, bags):
    """
    Describe: Check if bags allowed on new flight is no lower than number of bags requested by user
    Input: x: String or integer, number of bags allowed on flight to be appended
           bags: String or integer, number of bags requested by user
    Output: 1 if number of bags allowed on flight is no lower than number of bags requested by user, zero otherwise
    """
    if int(x)>=int(bags):
        return 1
    return 0

def outputFormatter(paths, bags, src, dst, mid_dst, is_return, is_multicity):
    """
    Describe: Formats paths to JSON compatible format
    Input: paths: List that contain paths (list) which are list of routes (list) containing flights (dict)
           bags: String or integer, number of bags requested by user
           src: String, source airport
           dst: String, final destination airport
           mid_dst: String, middle destination airport (when is_multicity==True)
           is_return: True / False
           is_multicity: True /False
    Output: final_paths: JSON object of final paths
    """
    final_paths = []

    for path in paths:
        full_path = {}
        flattened_path = [flight for one_way in path for flight in one_way]
        full_path["flights"] = flattened_path
        full_path["bags_allowed"] = min([int(flight["bags_allowed"]) for flight in flattened_path])
        full_path["bags_count"] = bags
        full_path["destination"] = dst
        if is_multicity == True:
            full_path["middle_destination"] = mid_dst
        full_path["origin"] = src
        full_path["total_price"] = sum([float(flight["base_price"]) for flight in flattened_path]) +\
                                    sum([float(flight["bag_price"])*bags for flight in flattened_path])
        if is_return == True:
            full_path["travel_time_to_{}".format(dst)] = \
                str(datetime.strptime(path[0][-1]["arrival"], "%Y-%m-%dT%H:%M:%S")
                                        - datetime.strptime(path[0][0]["departure"], "%Y-%m-%dT%H:%M:%S"))
            full_path["travel_time_to_{}".format(src)] = \
                str(datetime.strptime(path[-1][-1]["arrival"], "%Y-%m-%dT%H:%M:%S")
                                        - datetime.strptime(path[-1][0]["departure"], "%Y-%m-%dT%H:%M:%S"))
        elif is_multicity == True:
            full_path["travel_time_to_{}".format(mid_dst)] = \
                str(datetime.strptime(path[0][-1]["arrival"], "%Y-%m-%dT%H:%M:%S")
                                        - datetime.strptime(path[0][0]["departure"], "%Y-%m-%dT%H:%M:%S"))
            full_path["travel_time_to_{}".format(dst)] = \
                str(datetime.strptime(path[-1][-1]["arrival"], "%Y-%m-%dT%H:%M:%S")
                                        - datetime.strptime(path[-1][0]["departure"], "%Y-%m-%dT%H:%M:%S"))
        else:
            full_path["travel_time"] = \
                str(datetime.strptime(flattened_path[-1]["arrival"], "%Y-%m-%dT%H:%M:%S")
                                        - datetime.strptime(flattened_path[0]["departure"], "%Y-%m-%dT%H:%M:%S"))

        final_paths.append(full_path)

    final_paths = sorted(final_paths, key=lambda d: d["total_price"])

    final_paths = json.dumps(final_paths, indent=4)

    return final_paths

def findpaths(g, src, dst, mid_dst, bags, is_return, is_multicity, days_of_stay, max_layover_hours,
              max_travel_hours, max_nr_changes, day_of_departure):
    """
    Describe: Find paths in graph from source to destination using BFS algorithm
    Input: g: Dictionary with origins as keys and flights from the origins as values
           src: String, source airport
           dst: String, final destination airport
           mid_dst: String, middle destination airport (when is_multicity==True)
           bags: String or integer, number of bags requested by user
           is_return: True / False
           is_multicity: True / False
           days_of_stay: Integer, length of stay at destination/middle destination
           max_layover_hours: Integer, maximum layover hours between flights
           max_travel_hours: Integer, maximum travel hours in a route
           max_nr_changes: Integer, maximum number of changes in a route
           day_of_departure: String of departure with format %Y-%m-%d
    Output: final_paths: JSON object of final paths
    """
    # Create a queue which stores the paths
    q = deque()

    # Route vector to store the current route
    route = []
    route.append([{"origin":src, "destination":src}])
    q.append(route.copy())

    # List to store final paths
    final_paths = []

    if is_return == True:
        desired_dst = src
    else:
        desired_dst = dst

    while q:
        path = q.popleft()
        last = path[-1][-1]

        # If last vertex is the desired destination then add the path to final_paths

        if (last["destination"] == desired_dst) & (last["origin"] != last["destination"]):
            final_paths = addPath(path, final_paths)
        else:
            if (is_return == True) & (last["destination"] == dst) & (last["origin"] != last["destination"]):
                path.append([{"origin":dst, "destination":dst}])
            elif (is_multicity == True) & (last["destination"] == mid_dst) & (last["origin"] != last["destination"]):
                path.append([{"origin":mid_dst, "destination":mid_dst}])

            # Traverse to all the nodes connected to
            # current vertex and push new path to queue
            for i in range(len(g[last["destination"]])):
                if (isNotVisited(g[last["destination"]][i]["destination"], path)
                    & isLayoverCompatible(g[last["destination"]][i]["departure"], path, max_layover_hours)
                    & isStayLengthCompatible(g[last["destination"]][i]["departure"], path, days_of_stay)
                    & isTravelTimeCompatible(g[last["destination"]][i], path, max_travel_hours)
                    & isNrChangesCompatible(path, max_nr_changes)
                    & isDepartureDateCompatible(g[last["destination"]][i]["departure"], path, day_of_departure)
                    & isMultiCityCompatible(g[last["destination"]][i]["destination"], path, is_multicity, src, dst)
                    & isBagCompatible(g[last["destination"]][i]["bags_allowed"], bags)):
                    newpath = copy.deepcopy(path)
                    newpath[-1].append(g[last["destination"]][i])
                    q.append(newpath)

    # Restructure output to required format
    final_paths = outputFormatter(final_paths, bags, src, dst, mid_dst, is_return, is_multicity)

    return final_paths

# Driver code
if __name__ == "__main__":

    header_names = ['flight_no',
                     'origin',
                     'destination',
                     'departure',
                     'arrival',
                     'base_price',
                     'bag_price',
                     'bags_allowed']

    [path_to_csv, src, dst, bags,
    is_return, days_of_stay,
    max_layover_hours, max_travel_hours,
    max_nr_changes, day_of_departure,
    is_multicity, mid_dst] = parse_arguments()

    # Read data
    with open(path_to_csv, 'r') as flights:
        reader = csv.reader(flights)
        rows=[]
        header=[]
        for row in reader:
            if any(elem in row for elem in header_names):
                header = row
            else:
                rows.append(row)

    # Raise error if input data incorrect
    if set(header)!=set(header_names):
        missing_column = set(header_names) - set(header)
        print("Incorrect data set provided, the columns are missing: {}.".format(missing_column))
        sys.exit()

    # Raise error if any of src, dst, mid_dst are the same
    if src == dst:
        print("Source and destination cannot be the same city.")
        sys.exit()
    elif src == mid_dst:
        print("Source and middle destination cannot be the same city.")
        sys.exit()
    elif mid_dst == dst:
        print("Middle destination and final destination cannot be the same city.")
        sys.exit()

    # Raise error if return and multicity at the same time
    if (is_return==True) & (is_multicity==True):
        print("Trip cannot be return and multicity at the same time.")
        sys.exit()

    # Generate adjacency list
    g = generateAdjacencyDict(rows, header)

    # Define vertices from adjacency matrix
    vertices = g.keys()

    # Raise error if additional inputs are incorrect
    if src not in vertices:
        print("Incorrect source provided, source not found in dataset locations. Available locations: {}"
              .format(vertices))
        sys.exit()
    elif dst not in vertices:
        print("Incorrect destination provided, destination not found in dataset locations. Available locations: {}"
             .format(vertices))
        sys.exit()
    elif (is_multicity==True) & (mid_dst not in vertices):
        print("Incorrect middle destination provided, middle destination not found in dataset locations. Available locations: {}"
             .format(vertices))
        sys.exit()

    # Function for finding the paths
    final_paths_json = findpaths(g, src, dst, mid_dst, bags, is_return,
                       is_multicity, days_of_stay, max_layover_hours,
                       max_travel_hours, max_nr_changes,
                       day_of_departure)

    final_paths = json.loads(final_paths_json)
    
    if len(final_paths) == 0:
        print("No flight combinations match the specified parameters!")
    else:
        if is_return==True:
            print("path from src {} to dst {} to src {} are".format(
            src, dst, src))
        elif is_multicity==True:
            print("path from src {} to mid_dst {} to dst {} are".format(
            src, mid_dst, dst))
        else:
            print("path from src {} to dst {} are".format(
            src, dst))
        
        print(final_paths_json)
        print(len(final_paths))
