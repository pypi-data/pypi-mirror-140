import logging
import slack_alerts
import os

log = logging.getLogger(__name__)

class SlackRapper(object):
    def __init__(self, webhook_filename=None):
        """
        :param webhook_filename: The webhook filename pointing to a channel that you want to post a message to
        """
        self.slack_alerter = logging.getLogger(__name__)
        try:
            env = os.environ["NODE_ENV"]
        except: 
            env = None
        try:
            self.filename = webhook_filename
            with open(self.filename, 'r') as file:
                webhook = file.read()
            self.slack_alerter = slack_alerts.Alerter('{}'.format(webhook))
        except (TypeError, FileNotFoundError) as e:
            self.slack_alerter.error(f'Type or file not found error, using default logger')
            if env not in['dev', None]:
                raise e
            
    def notify(self, message):
        self.slack_alerter.info(message)