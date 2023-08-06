# stoy
Application for shutting down kernels in Jupyter Lab after they were idle for a specified period of time.
The jupyter instance itself is terminated when no kernels were open for some time.

# Installation
Install with `pip`
```commandline
pip install stoy
```

# Usage
Define the three timeouts, in seconds, as demonstrated in the example below:
```commandline
stoy --kernel-idle=3600 --server-idle=1800 &
```

# Troubleshooting
The application saves logs in `~/.stoy/stoy.log` unless a different location is specified using the `--log` argument. 
To access the logs open jupyter lab terminal and run:
```commandline
cat ~/.stoy/stoy.log
```
or 
```commandline
tail -n 20 ~/.stoy/stoy.log
```
