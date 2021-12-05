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
 - angle
 - restricted subgraph (https://arxiv.org/pdf/2107.11318.pdf)
 
 
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
 python main.py --days 7 --matching_method angle --routing_method insertion --vehicles 1000
 ```
 
 ## Result
 
 ![image](https://user-images.githubusercontent.com/28619620/144733396-b210dd94-4c70-45d1-bb85-c10eda1dc90e.png)
 
