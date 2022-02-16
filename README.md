# Entry task for Python weekend in Budapest - 2022 March

** The Python script (solutions.py) prints out a structured list of all flight combinations for a selected route between airports A -> B, sorted by the final price for the trip, using flight data in a form of `csv` file.**

### Description
The input dataset need to contain the following columns:
- `flight_no`: Flight number.
- `origin`, `destination`: Airport codes.
- `departure`, `arrival`: Dates and times of the departures/arrivals.
- `base_price`, `bag_price`: Prices of the ticket and one piece of baggage.
- `bags_allowed`: Number of allowed pieces of baggage for the flight.

In addition to the dataset, the script takes some additional arguments as input:

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `origin`      | string  | Origin airport code.      |                              |
| `destination` | string  | Destination airport code. |                              |
| `bags`        | integer | Number of requested bags. | Optional (defaults to 0)     |
| `return`      | boolean | Is it a return flight?   | Optional (defaults to false) |
| `days_of_stay`        | integer | In case of return trip, minimum days of stay at destination. In case of multicity trip, minimum days of stay at mid stop.| Optional (defaults to 0)     |
| `max_layover_hours`        | integer | Maximum layover hours between flights. | Optional (defaults to 6)     |
| `max_travel_hours`        | integer | Maximum travel hours in a route. 0 for no restrictions. | Optional (defaults to 0)     |
| `max_nr_changes`        | integer | Maximum number of changes in a route.  0 for direct flights only, -1 for no restrictions. | Optional (defaults to -1)     |
| `day_of_departure`        | string | String of departure with format %Y-%m-%d.  | Optional (defaults to '')     |
| `multicity`      | boolean | Is it a multicity flight?   | Optional (defaults to false) |
| `middle_destination`        | string | Middle destination ariport code in case of multicity trip.| Optional (defaults to '')     |


##### Performing trip search

```
python -m solution <path_to_dataset> <origin> <destination> [--bags=<number>] [--return] [--days_of_stay=<number>] [--max_layover_hours=<number>]  [--max_travel_hours=<number>]  [--max_nr_changes=<number>] [--day_of_departure=<string>] [--multicity]
[--middle_destination=<string>]
```

##### Notes

- Trip cannot be return and multicity at the same time
- Maximum travel time defines restriction for one way flight of a trip

#### Output
The output will be a json-compatible structured list of trips sorted by price. The trip has the following schema:
| Field          | Description                                                   | Notes                        |
|----------------|---------------------------------------------------------------|------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |                              |
| `origin`       | Origin airport of the trip.                                   |                              |
| `destination`  | The final destination of the trip.                            |                              |
| `bags_allowed` | The number of allowed bags for the trip.                      |                              |
| `bags_count`   | The searched number of bags.                                  |                              |
| `total_price`  | The total price for the trip.                                 |                              |
| `travel_time`  | The total travel time.                                        |                              |
| `travel_time_to_<destination>`  | The total travel time to destination.                                        |                              |
| `travel_time_to_<origin>`  | The total travel time to origin.                                       |                              |
| `travel_time_to_<middle_destination>`  | The total travel time to middle_destination.                                        |                              |


**For more information, check the example section.**


## Example behaviour

Let's imagine we wrote our solution into one file, `solution.py` and our datatset is in `data.csv`.
We want to test the script by performing a flight search on route BTW -> REJ (we know the airports are present in the dataset) with one bag. We run the thing:

```bash
python -m solution example/example0.csv BTW REJ --bags=1
```
and get the following result:

```json

```
