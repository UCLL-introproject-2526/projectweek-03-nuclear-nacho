import json

with open("scores.json", "w") as f:
    json.dump([], f, indent=4)
