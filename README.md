# Simple-Ride-Pooling-Simulator

<b>Ride-pooling simulator for evaluating matching and routing
algorithms.</b>



request data:
https://drive.google.com/file/d/1P7tAfJ4hG91H-gXBeL-b3C22eyXD8hdb/view?usp=sharing

precalculated shortest paths:
https://drive.google.com/file/d/1LztpfhNMtibB7oPxVmKtdTCqL1vh-oet/view?usp=sharing

you can get paths.pickle by running generate_pickle.py but it will takes more than a day. I recommand you to download a file above.

 ## Options
 
 matching method:
 - greedy
 - restricted subgraph (https://arxiv.org/pdf/2107.11318.pdf)
 - angle (our own heuristic!)!
 [KakaoTalk_20211219_131041277](https://user-images.githubusercontent.com/28619620/147720676-9d492c3b-4411-4d57-b5dd-e6726bbb2253.jpg)

 
 
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
 python main.py --days 7 --matching_method greedy --routing_method insertion --supply under
 ```
 
 ## Metrics
 
 ## Result
 
![image](https://user-images.githubusercontent.com/28619620/144892474-f0746a46-f109-4c88-8ce6-603bf3bc2eee.png)
{"serve_time": 47.28, "occupancy_rate": 0.42, "waiting_time": 154.66, "detour_time": 297.15, "accept_rate": 0.61, "throughput": 152.4, "utilization": 0.18, "sys_efficiency": 14.19, "customer_score": 2.21}
