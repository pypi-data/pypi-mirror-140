# stockeasy
Quick and Easy Stock Portfolio Analysis - FOR ENTERTAINMENT PURPOSES ONLY!!

### Note
I use Docker for enviroment management; as such, my build process will deviate from more classical approaches. 

## Getting Started Developing
for windows create a env.bat file after pulling with the mount path to the current directory. In windows, you can't use relative paths with Docker Volume mounts, so...

```
set LOCAL_MOUNT=C:\Users\ablac\OneDrive\Documents\stockeasy\
```

then run

```
make DOCKER
```

### Available doit tasks
lint            -- runs linting
setup_tool      -- installs local tool
unit_tests      -- runs unit tests
