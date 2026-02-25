# SamuParser
A python script using ballchasing API to parse rocket league replay files and feed SamuTracker.

## Save RL game replays
Saved RL games replays can be found in `~/Documents/My Games/Rocket League/TAGame/DemosEpic/`. Copy them to the `raw` folder of this project.

## Convert RL .replay files
Using ballchasing.com API.

```
python main.py --convert
```

## Merge parsed replays
```
python main.py --merge
```

## Feed the merged main.pkl file to SamuTracker
github.com/Potamochoerus/SamuTracker