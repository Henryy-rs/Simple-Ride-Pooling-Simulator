import pandas as pd
import matplotlib.pyplot as plt
from engine.osm import OSMEngine
from request.request_loader import RequestLoader

# df = pd.read_csv("C:/deep/RidePooling-Simulator/results/radian+insertion, n_vehicles=500/logs.csv")
# df = df['location'].value_counts().head(20)
# print(df)
# # df["location"].hist(bins=4527)
# # plt.show()
engine = OSMEngine(network_path="data/Manhattan.graphml", paths="paths.pickle")
# for value in df.index:
#     print(engine.mapping[value])
rl = RequestLoader("data/db.sqlite3")
rl.iter_request(current_time=1464753600 + 3600 * 5, timestep=60, engine=engine)