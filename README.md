# Simple-Ride-Pooling-Simulator

<b>Ride-pooling simulator for evaluating matching and routing
algorithms.</b>



request data:
https://drive.google.com/file/d/1UzVdbA3cSsC22pHTSUliq5ORgm6LB7Rd/view?usp=sharing

precalculated shortest paths:
https://drive.google.com/file/d/1LztpfhNMtibB7oPxVmKtdTCqL1vh-oet/view?usp=sharing

you can get paths.pickle by running generate_pickle.py but it will takes more than a day. I recommand you to download a file above.

## Usage

 ```bash
 
    pip install osmnx
    
    python main.py

 ```
 
 options
 
 ```bash
 python main.py --routing_method insertion --vehicles 1000
 ```
## TODO

- logger
- visualization
- implement a new algorithm ~ 11.xx
