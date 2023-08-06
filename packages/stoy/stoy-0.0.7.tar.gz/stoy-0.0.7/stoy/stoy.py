import os
import aiohttp
import asyncio
import subprocess
import time
import datetime
import logging
import argparse


URL = "http://localhost:8888"
SLEEP_SECONDS = 5


def parse_arguments():
    parser = argparse.ArgumentParser(description="Automatically stop jupyter kernels and the server when idle for"
                                     " a specified period of time")
    parser.add_argument("--kernel-idle", "-k",
                        help="Number of seconds for the kernel to remain idle before it is deleted. Default is 3600.",
                        required=False,
                        type=float,
                        default=3600.0)
    parser.add_argument("--terminal-idle", "-t",
                        help="Number of seconds for the terminal to remain idle before it is deleted. Default is 3600.",
                        required=False,
                        type=float,
                        default=3600.0)
    parser.add_argument("--server-idle", "-s",
                        help="Number of seconds for the server to run with no kernels and terminals "
                             "before it is deleted. Default is 1800.",
                        required=False,
                        type=float,
                        default=1800.0)
    parser.add_argument("--path", "-p",
                        help="Path to directory containing jupyter lab. Required if jupyter lab is not in system path.",
                        required=False,
                        type=str,
                        default="")
    parser.add_argument("--shutdown",
                        help="Shutdown the machine",
                        action="store_true",
                        default=False)

    return parser.parse_args()


def prepare_log():
    home = os.path.expanduser("~")
    log_dir = os.path.join(home, ".stoy")
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    log_file = os.path.join(log_dir, "stoy.log")
    return log_file


def get_token(jupyter_path):
    pattern = "?token="
    running = False
    while not running:
        cmd = "jupyter"
        if len(jupyter_path) > 0:
            cmd = os.path.join(jupyter_path, cmd)
        result = subprocess.run([cmd, "lab", "list"], stdout=subprocess.PIPE)
        if result.returncode != 0:
            logging.error(f"Command 'jupyter lab list' failed with exit code {result.returncode}")
            exit(1)
        msg = result.stdout.decode("utf-8")
        loc = msg.find(pattern)
        if loc == -1:
            time.sleep(5.0)
            logging.debug("Jupyter lab server is not running")
            continue
        t, *rest = msg[loc:].split(" ")
        logging.debug(t[1:])
        return t[1:]


def inactive_seconds(entity):
    now = datetime.datetime.utcnow()
    la = entity["last_activity"]
    # dt = datetime.datetime.fromisoformat(la[:-1])
    fmt = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(la[:-8], fmt)
    delta = now - dt
    return delta.total_seconds()


async def run(url, token, terminal_timeout, kernel_timeout, server_timeout, shutdown):
    async with aiohttp.ClientSession() as session:
        running = True
        terminal_count = 0
        kernel_count = 0
        inactive_since = None
        while running:
            async with session.get(f"{url}/api/terminals", params=token) as resp:
                terminals = await resp.json()
                terminal_count = len(terminals)
                for terminal in terminals:
                    name = terminal['name']
                    seconds = inactive_seconds(terminal)
                    logging.debug(f"terminal {name} inactive for {seconds} s")
                    if seconds > terminal_timeout:
                        async with session.delete(f"{url}/api/terminals/{name}", params=token) as r2:
                            if r2.status == 204:
                                logging.debug(f"terminal {name} deleted")
                            else:
                                logging.error(f"terminal {name} deletion failed with status {r2.status}")

            async with session.get(f"{url}/api/kernels", params=token) as resp:
                kernels = await resp.json()
                kernel_count = len(kernels)
                for kernel in kernels:
                    kid = kernel["id"]
                    seconds = inactive_seconds(kernel)
                    logging.debug(f"kernel {kid} inactive for {seconds} s")
                    if seconds > kernel_timeout:
                        async with session.delete(f"{url}/api/kernels/{kid}", params=token) as r2:
                            if r2.status == 204:
                                logging.debug(f"kernel {kid} deleted")
                            else:
                                logging.error(f"kernel {kid} deletion failed with status {r2.status}")
            if kernel_count == 0 and terminal_count == 0:
                if inactive_since is None:
                    inactive_since = datetime.datetime.utcnow()
                    logging.debug("no active kernels or terminals")
                dt = datetime.datetime.utcnow() - inactive_since
                if dt.total_seconds() > server_timeout:
                    logging.debug("Shutting down jupyter server")
                    r = subprocess.run(["pgrep", "jupyter"], stdout=subprocess.PIPE)
                    pid, *rest = r.stdout.decode().split("\n")
                    if len(pid) > 0:
                        logging.debug(f"jupyter server PID={pid}")
                        r = subprocess.run(["kill", pid])
                        if r.returncode == 0:
                            logging.debug(f"jupyter server terminated")
                        else:
                            logging.error(f"failed to terminate jupyter server.`kill` exited with code {r.returncode}")
                            exit(3)
                    else:
                        logging.error("Unable to find PID of jupyter server")
                        exit(2)
                    running = False

            if kernel_count > 0 or terminal_count > 0:
                inactive_since = None

            await asyncio.sleep(SLEEP_SECONDS)

    if shutdown:
        logging.debug("shutting down the instance")
        subprocess.Popen(["shutdown"])

    logging.debug("done")


def main():
    args = parse_arguments()
    logging.basicConfig(filename=prepare_log(),
                        filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.DEBUG)
    jupyter_token = get_token(args.path)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(url=URL,
                                    token=jupyter_token,
                                    kernel_timeout=args.kernel_idle,
                                    terminal_timeout=args.terminal_idle,
                                    server_timeout=args.server_idle,
                                    shutdown=args.shutdown))
    except KeyboardInterrupt:
        logging.info("terminated by the user")
    except RuntimeError as e:
        logging.error(f"Unknown error: {str(e)}")
        exit(3)


if __name__ == "__main__":
    main()
