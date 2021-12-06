# Simple-Ride-Pooling-Simulator

<b>Ride-pooling simulator for evaluating matching and routing
algorithms.</b>



request data:
https://drive.google.com/file/d/1P7tAfJ4hG91H-gXBeL-b3C22eyXD8hdb/view?usp=sharing

precalculated shortest paths:
https://drive.google.com/file/d/1LztpfhNMtibB7oPxVmKtdTCqL1vh-oet/view?usp=sharing

you can get paths.pickle by running generate_pickle.py but it will takes more than a day. I recommand you to download a file above.

 ## options
 
 matching method:
 - greedy
 - angle (our own heuristic!)
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
 python main.py --days 7 --matching_method angle --routing_method insertion --supply under
 ```
 
 ## Result
 
![image](https://user-images.githubusercontent.com/28619620/144892474-f0746a46-f109-4c88-8ce6-603bf3bc2eee.png)
 
