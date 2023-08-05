import argparse
import json
import pyzantium
import flask

app = flask.Flask("Pyzantium")


def init_config(out: str):
    settings = {
        "address": "127.0.0.1",
        "port": "3500",
        "storage": {"type": "disk", "dir": "./bchain", "index": True},
        "consensus": "pow",
        "mining": {"enabled": "false"},
    }
    with open(out, "w+") as fout:
        json.dump(settings, fout, indent=2)


@app.get("/info")
def chain_info():
    return flask.jsonify({'info':'ok'})


def main():
    args = argparse.ArgumentParser(
        "node",
        description="Simple blockchain node over HTTP",
        epilog="WARNNING: Don't use in production",
    )

    args.add_argument("-c", help="Configuration file", metavar="config")
    args.add_argument(
        "-i", help="Initialize a config file with default settings", metavar="out"
    )

    arguments = args.parse_args()

    if arguments.i:
        init_config(arguments.i)

    app.run("127.0.0.1", 3500)


if __name__ == "__main__":
    main()
