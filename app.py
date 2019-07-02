import os
import re
import subprocess
import time

from dhooks import Embed, Webhook


class PerforceLogger:
    def __init__(self, webhook_url):
        """ Initializes a 30 second timer used to check if commits have been made.  """
        self.webhook_url = webhook_url
        self.global_store = {
            'latest_change': ''
        }

    def check_p4(self):
        """ Runs the p4 changes command to get the latest commits from the server. """
        p4_changes = subprocess.Popen('p4 changes -t -m 1 -l', stdout=subprocess.PIPE, shell=True)
        return p4_changes.stdout.read().decode('ISO-8859-1')

    def check_for_changes(self, output):
        """ Figures out if the latest p4 change is new or should be thrown out. """
        if output != self.global_store['latest_change']:
            self.global_store['latest_change'] = output

            if '*pending*' in output:
                return ''

            else:
                return output

        else:
            return ''

    def post_changes(self):
        """ Posts the changes to the Discord server via a webhook. """
        regex = r"Change (?P<change_number>\d) on (?P<date>\d{4}/\d{2}/\d{2}) by (?P<name>.*)@.* \'(?P<message>.*?)\'"
        substitution = "\g<message>- \g<name>"

        message = re.sub(regex, substitution, self.check_p4(), flags=re.MULTILINE)

        output = self.check_p4()
        payload = self.check_for_changes(output)
        if payload != '':
            # Make webhook embed
            hook = Webhook(self.webhook_url)

            embed = Embed(
                description=message,
                color=49915,
                timestamp="now"
            )
            # Post to channel
            hook.send(embed=embed, username="Perforce", avatar_url="https://i.imgur.com/WseNTPC.jpg")
        else:
            return


if __name__ == "__main__":
    """ Initializes the application loop that checks Perforce for changes. """
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
    logger = PerforceLogger(DISCORD_WEBHOOK_URL)
    timer = time.time()

    while True:
        logger.post_changes()
        time.sleep(30.0 - ((time.time() - timer) % 30.0))
