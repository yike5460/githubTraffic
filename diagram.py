import json
import matplotlib.pyplot as plt
import datetime

# Load the JSON file
with open('views.json') as f:
    data = json.load(f)

# Extract the data to plot
dates = []
uniques = []
views = []
for entry in data[0]:
    print(entry)
    # convert "timestamp": "2023-03-23T00:00:00Z", to a datetime object
    dates.append(datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))
    uniques.append(int(entry['uniques']))
    views.append(int(entry['views']) if entry['views'] is not None else 0)

# Create the chart with x-axis more wide
plt.figure(figsize=(20, 10))
plt.plot(dates, uniques, label='uniques')
plt.plot(dates, views, label='views')
plt.legend()
plt.show()
