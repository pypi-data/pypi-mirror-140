import os
import aiohttp
import asyncio
import datetime
import logging
import argparse
import json
import boto3


URL = "https://localhost:8443"
SLEEP_SECONDS = 5


def parse_arguments():
    parser = argparse.ArgumentParser(description="Automatically stop jupyter kernels and the server when idle for"
                                     " a specified period of time")
    parser.add_argument("--version", "-v",
                        help="Print version number",
                        action="store_true",
                        default=False)
    parser.add_argument("--url", "-u",
                        help=f"Jupyter URL. Default is '{URL}'",
                        required=False,
                        type=str,
                        default=URL)
    parser.add_argument("--token", "-t",
                        help="Jupyter token",
                        required=False,
                        type=str,
                        default="")
    parser.add_argument("--kernel-idle", "-k",
                        help="Number of seconds for the kernel to remain idle before it is deleted. Default is 3600.",
                        required=False,
                        type=float,
                        default=3600.0)
    parser.add_argument("--server-idle", "-s",
                        help="Number of seconds for the server to run with no kernels and terminals "
                             "before it is deleted. Default is 1800.",
                        required=False,
                        type=float,
                        default=1800.0)
    parser.add_argument("--log", "-l",
                        help="Path to log directory. If not provided the logs are saved in ~/.stoy",
                        required=False,
                        type=str,
                        default="")

    return parser.parse_args()


def prepare_log(log_directory):
    if len(log_directory) > 0 and os.path.isdir(log_directory):
        log_dir = log_directory
    else:
        home = os.path.expanduser("~")
        log_dir = os.path.join(home, ".stoy")
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
    log_file = os.path.join(log_dir, "stoy.log")
    return log_file


def inactive_seconds(entity):
    now = datetime.datetime.utcnow()
    la = entity["last_activity"]
    fmt = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(la[:-8], fmt)
    delta = now - dt
    return delta.total_seconds()


def get_notebook_name():
    filename = "/opt/ml/metadata/resource-metadata.json"
    with open(filename, "r") as f:
        meta = json.load(f)
    return meta["ResourceName"]


async def run(url, kernel_timeout, server_timeout, token=""):
    async with aiohttp.ClientSession() as session:
        running = True
        inactive_since = None
        params = dict()
        if len(token) > 0:
            params["token"] = token
            logging.debug(f'using token "{token}"')
        while running:
            try:
                kernels_url = f"{url}/api/kernels"
                async with session.get(kernels_url, params=params, ssl=False) as resp:
                    if resp.status != 200:
                        logging.error(f'GET "{kernels_url}" returned {resp.status}')
                        exit(2)
                    kernels = await resp.json()
                    kernel_count = len(kernels)
                    for kernel in kernels:
                        kid = kernel["id"]
                        seconds = inactive_seconds(kernel)
                        logging.debug(f"kernel {kid} inactive for {seconds} s")
                        if seconds > kernel_timeout:
                            async with session.delete(f"{url}/api/kernels/{kid}", params=params, ssl=False) as r2:
                                if r2.status == 204:
                                    logging.debug(f"kernel {kid} deleted")
                                else:
                                    r = await r2.json()
                                    logging.error(f"kernel {kid} deletion failed with status {r2.status}: '{r}'")
            except aiohttp.client_exceptions.ClientConnectorError:
                logging.info(f"connection to '{url}/api/kernels' failed")
                await asyncio.sleep(SLEEP_SECONDS)
                continue

            if kernel_count == 0:
                if inactive_since is None:
                    inactive_since = datetime.datetime.utcnow()
                    logging.debug("no active kernels")
                dt = datetime.datetime.utcnow() - inactive_since
                if dt.total_seconds() > server_timeout:
                    name = get_notebook_name()
                    logging.debug(f"shutting down instance '{name}'")
                    client = boto3.client("sagemaker")
                    client.stop_notebook_instance(NotebookInstanceName=name)
                    break
            else:
                inactive_since = None

            await asyncio.sleep(SLEEP_SECONDS)

    logging.debug("done")


def main():
    args = parse_arguments()

    if args.version:
        with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
            v = version_file.read().strip()
            print(f"version {v}")
            exit(0)

    log_file = prepare_log(args.log)
    print(f"log file: '{log_file}'")
    logging.basicConfig(filename=log_file,
                        filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.DEBUG)
    logging.debug("started")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(url=args.url,
                                    kernel_timeout=args.kernel_idle,
                                    server_timeout=args.server_idle,
                                    token=args.token))
    except KeyboardInterrupt:
        logging.info("terminated by the user")
    except RuntimeError as e:
        logging.error(f"Unknown error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
