import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s",
)


from . import config_utils as Config
from . import env_utils as Env
from . import github_api as Gh
from . import output_utils as Output

OUTPUT_FILENAME = "output.txt"
DUMP_CONFIG_WHEN_TRIGGERED = False

if __name__ == "__main__":
    logging.info("Starting BeyondSilence")
    config = Config.config
    output = ""

    DUMP_CONFIG_WHEN_TRIGGERED = config["dump_config_when_triggered"]

    # Get user name
    user_name = config["github_user_name"]

    # Get days of inactivity
    days = Gh.get_days_of_inactivity(user_name)

    # Get days before
    days_before = config["days_before"]

    if days > days_before:
        # Triggered
        logging.info(
            f"User {user_name} has been inactive for {days} days, triggering..."
        )
        output = Output.gen_triggered_output(config)
        logging.info(output)
        # Rewrite README.md with new output
        Output.save_output("```\n" + output + "\n```", "README.md")

        if DUMP_CONFIG_WHEN_TRIGGERED:
            logging.info("Dumping config")
            Output.save_output(json.dumps(config), "config.json")
    else:
        # Not triggered
        logging.info("Everything is fine")
        output = Output.gen_regular_output()
        logging.info(output)

    # Save output
    logging.info(f"Saving output to {OUTPUT_FILENAME}")
    Output.save_output(output, OUTPUT_FILENAME)

    logging.info("Ending BeyondSilence")
