# Simple-Ride-Pooling-Simulator

<b>Ride-pooling simulator for evaluating matching and routing
algorithms.</b>



request data:
https://drive.google.com/file/d/1UzVdbA3cSsC22pHTSUliq5ORgm6LB7Rd/view?usp=sharing

precalculated shortest paths:
https://drive.google.com/file/d/1LztpfhNMtibB7oPxVmKtdTCqL1vh-oet/view?usp=sharing

you can get paths.pickle by running generate_pickle.py but it will takes more than a day. I recommand you to download a file above.

 ## options
 
 matching method:
 - greedy
 - radian
 - restricted subgraph
 
 routing method:
 - greedy
 - insertion

## Usage

 ```bash
 
    pip install osmnx
    
    python main.py

 ```

example
 
 ```bash
 python main.py --days 7 --matching_method radian --routing_method insertion --vehicles 1000
 ```
## TODO

- logger
- implement a matching algorithm ~ 12.07
