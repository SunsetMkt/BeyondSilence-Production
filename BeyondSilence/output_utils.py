import logging
import time
import os

from . import env_utils as Env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s",
)

# Magic number for output file
# BSOK : BeyondSilence OK
# BSTR : BeyondSilence Triggered
# BSER : BeyondSilence Error (Unused)


def gen_regular_output():
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f"BSOK\nLast update time: {now_time}, everything is OK"


def gen_triggered_output(config):
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    output = f'BSTR\nGitHub user name: {config["github_user_name"]}' + "\n\n"
    output += (
        f'Last update time: {now_time}, triggered by inactivity of {config["days_before"]} days'
        + "\n\n"
    )
    output += f'Main description:\n{config["main_description"]}' + "\n\n"
    output += f"Messages:\n"
    for message in config["messages"]:
        output += f"{message['environ']}: {message['description']}\n"
        real_value = message["content"]
        if real_value:
            output += f"Value: {real_value}\n"
        else:
            output += "Value: [environ unset]\n"
        output += "\n"
    output += "End of output\n"
    return output


def save_output(text, filename):
    logging.info(f"Save output to {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    abs_path = os.path.abspath(filename)
    logging.info(f"Output saved to {abs_path}")
