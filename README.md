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

| Argument name | type    | Description        | Notes                        |
|---------------|---------|--------------------|------------------------------|
| `origin`      | string  | Origin airport code.      |                              |
| `destination` | string  | Destination airport code. |                              |
| `bags`        | integer | Number of requested bags. | Optional (defaults to 0)     |
| `return`      | boolean | Is it a return flight?   | Optional (defaults to false) |
| `min_days_of_stay`        | integer | In case of return trip, minimum days of stay at destination. In case of multicity trip, minimum days of stay at middle stop.| Optional (defaults to 0)     |
| `max_layover_hours`        | integer | Maximum layover hours between flights. | Optional (defaults to 6)     |
| `max_travel_hours`        | integer | Maximum travel hours in a route. 0 for no restrictions. | Optional (defaults to 0)     |
| `max_nr_changes`        | integer | Maximum number of changes in a route.  0 for direct flights only, -1 for no restrictions. | Optional (defaults to -1)     |
| `day_of_departure`        | string | String of departure with format %Y-%m-%d.  | Optional (defaults to "")     |
| `multicity`      | boolean | Is it a multicity flight?   | Optional (defaults to false) |
| `middle_destination`        | string | Middle destination ariport code in case of multicity trip.| Optional (defaults to "")     |

##### Notes

- Trip cannot be return and multicity at the same time.
- Maximum travel hours and maximum number of changes defines restriction for one way route of a trip.
- Airports do not repeat on the same route.
- When performing multicity trip, source and destination airports do not repeat. For example, when origin is BDP, middle destination is LDN and destination is BCN, then BDP -> LDN -> BDP ->BCN is not a valid journey.


##### Performing trip search

```
python -m solution <path_to_dataset> <origin> <destination> [--bags=<number>] [--return] [--min_days_of_stay=<number>] [--max_layover_hours=<number>]  [--max_travel_hours=<number>]  [--max_nr_changes=<number>] [--day_of_departure=<string>] [--multicity]
[--middle_destination=<string>]
```

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
| `travel_time`  | The total travel time.                                        |  Present when journey is one-way                            |
| `travel_time_to_<destination>`  | The total travel time to destination.                                        |  Present when journey is return or multicity                            |
| `travel_time_to_<origin>`  | The total travel time to origin.                                       |  Present when journey is return                             |
| `travel_time_to_<middle_destination>`  | The total travel time to middle_destination.                                        |  Present when journey is multicity                             |


**For more information, check the example section.**


## Example behaviour

To perform a flight search on route GXV -> IUT (we know the airports are present in the dataset) with two bags, maximum 5 hours layover, multicity with middle destination LOM and minimum 9 days of stay at the middle destination, we run the following:

```bash
python3 -m solution example/example2.csv GXV IUT --bags=2 --multicity --middle_destination=LOM --min_days_of_stay=9 --max_layover_hours=5
```
and get the following result:

```json
[
    {
        "flights": [
            {
                "flight_no": "SJ497",
                "origin": "GXV",
                "destination": "LOM",
                "departure": "2021-09-01T14:30:00",
                "arrival": "2021-09-01T16:15:00",
                "base_price": "16.0",
                "bag_price": "14",
                "bags_allowed": "2"
            },
            {
                "flight_no": "SJ609",
                "origin": "LOM",
                "destination": "IUT",
                "departure": "2021-09-13T22:35:00",
                "arrival": "2021-09-14T00:50:00",
                "base_price": "48.0",
                "bag_price": "14",
                "bags_allowed": "2"
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "IUT",
        "middle_destination": "LOM",
        "origin": "GXV",
        "total_price": 120.0,
        "travel_time_to_LOM": "1:45:00",
        "travel_time_to_IUT": "2:15:00"
    },
    {
        "flights": [
            {
                "flight_no": "SJ497",
                "origin": "GXV",
                "destination": "LOM",
                "departure": "2021-09-03T14:30:00",
                "arrival": "2021-09-03T16:15:00",
                "base_price": "16.0",
                "bag_price": "14",
                "bags_allowed": "2"
            },
            {
                "flight_no": "SJ609",
                "origin": "LOM",
                "destination": "IUT",
                "departure": "2021-09-13T22:35:00",
                "arrival": "2021-09-14T00:50:00",
                "base_price": "48.0",
                "bag_price": "14",
                "bags_allowed": "2"
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "IUT",
        "middle_destination": "LOM",
        "origin": "GXV",
        "total_price": 120.0,
        "travel_time_to_LOM": "1:45:00",
        "travel_time_to_IUT": "2:15:00"
    },
    {
        "flights": [
            {
                "flight_no": "DX390",
                "origin": "GXV",
                "destination": "YOT",
                "departure": "2021-09-01T19:15:00",
                "arrival": "2021-09-01T23:20:00",
                "base_price": "133.0",
                "bag_price": "9",
                "bags_allowed": "2"
            },
            {
                "flight_no": "QG767",
                "origin": "YOT",
                "destination": "LOM",
                "departure": "2021-09-02T00:55:00",
                "arrival": "2021-09-02T06:45:00",
                "base_price": "357.0",
                "bag_price": "10",
                "bags_allowed": "2"
            },
            {
                "flight_no": "SJ609",
                "origin": "LOM",
                "destination": "IUT",
                "departure": "2021-09-13T22:35:00",
                "arrival": "2021-09-14T00:50:00",
                "base_price": "48.0",
                "bag_price": "14",
                "bags_allowed": "2"
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "IUT",
        "middle_destination": "LOM",
        "origin": "GXV",
        "total_price": 604.0,
        "travel_time_to_LOM": "11:30:00",
        "travel_time_to_IUT": "2:15:00"
    }
]

```
