# stockeasy
Quick and Easy Stock Portfolio Analysis - FOR ENTERTAINMENT PURPOSES ONLY!!

## Introduction
All exposed functions in this package have been designed with the intent that they can be strung together in a DAG; as such, they all follow a consistent contract.

### function contract
```
def function_name (data: Dict, config: dict, logging: logging.Logger)
return results: dict
```

### data contract
```
data = {'name': pandas dataframe}
```

### config contract
```
config = {'setting': setting values}
```
### Example Code
```
import stockeasy
import pandas as pd

df_stocklist = pd.DataFrame([['VTSAX', 120], ['MSFT', 100]], columns=['symbol', 'sharesOwned'])

config = {
    'symbolField': 'symbol',
    'sharesField': 'sharesOwned',
    'dataFields': ['exchange', 'symbol', 'shortName', 'sector', 'country', 'marketCap']
}

results = stockeasy.get_info({'input': df_stocklist}, config=config)

print(results.get('output').head())
```

### logging
Standard python logging object


### Notes
- I use Docker for enviroment management; as such, my build process will deviate from more classical approaches.
- I attempt to follow functional programming style

## Getting Started Contributing
for windows create a env.bat file after pulling with the mount path to the current directory. In windows, you can't use relative paths with Docker Volume mounts, so...

```
set LOCAL_MOUNT=C:\Users\ablac\OneDrive\Documents\stockeasy\
```

then run

```
make DOCKER
cd stockeasy
doit
```

### Available doit tasks
lint            -- runs linting
setup_tool      -- installs local tool
unit_tests      -- runs unit tests
