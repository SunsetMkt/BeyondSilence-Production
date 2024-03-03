import base64
import json
import sys


def gen_env(envname, filename):
    with open(filename, "r", encoding="utf-8") as f:
        config = json.load(f)

    config_str = json.dumps(config)

    config_str = base64.b64encode(config_str.encode("utf-8")).decode("utf-8")

    # If config_str is larger than 48 KB
    if sys.getsizeof(config_str) > 48 * 1024:
        raise Exception(f"{envname} is larger than 48 KB")

    print(f"{envname}={config_str}")
    print()


if __name__ == "__main__":
    gen_env("BEYONDSILENCE_CONFIG", "config.example.json")
    gen_env("BEYONDSILENCE_KEYS", "keys.example.json")
