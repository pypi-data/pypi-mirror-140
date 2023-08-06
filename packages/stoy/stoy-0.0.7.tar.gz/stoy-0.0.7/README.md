# stoy
Application for shutting down kernels and terminals in Jupyter Lab after they were idle for a specified period of time.
Jupyter Lab itself is terminated when no kernels and terminals were open for some time.

# Installation
Install with `pip`
```commandline
pip install stoy
```

# Usage
Define the three timeouts, in seconds, as demonstrated in the example below:
```commandline
stoy --kernel-idle=3600 --terminal-idle=3600 --server-idle=1800 &
```
If `jupyter lab` is not in the system path you will need to provide it as an optional parameter, for example:
```commandline
stoy --kernel-idle=3600 --terminal-idle=3600 --server-idle=1800 --path="/home/ec2-user/anaconda3/bin" &
```
If you run the script in the cloud and wish to shut down the instance use the optional `--shutdown` flag. This option
requires that the script is run by a super user (use `sudo` when in doubt).

# Troubleshooting
The application saves logs in `~/.stoy/stoy.log`. To access the logs open jupyter lab terminal and run:
```commandline
cat ~/.stoy/stoy.log
```
or 
```commandline
tail -n 20 ~/.stoy/stoy.log
```


