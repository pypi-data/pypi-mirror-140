from pypers.steps.base.step_generic import EmptyStep
from pypers.core.interfaces.db import get_cron_db, get_operation_db
from pypers.core.interfaces import msgbus
import os
import time


class Submit(EmptyStep):
    """
    Triggers the fetch pipelines based on the db conf. Monitors the execution of them.
    Once all the triggered pipelines are done, it sends the publish message
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Triggers the fetch pipelines based on the db conf. Monitors the execution of them. Once all the triggered pipelines are done, it sends the publish message"
        ],
    }


    def check_still_running(self):
        for coll in get_operation_db().get_run(self.run_id):
            if coll.get('pipeline_status', None) == 'RUNNING':
                return True
        return False



    def process(self):
        cron_tab = get_cron_db().read_config()
        # Create the monitoring
        get_operation_db().create_run(self.run_id, cron_tab)
        # Trigger the messages
        for collection in cron_tab:
            output_dir = os.path.join(os.environ['WORK_DIR'],
                                      self.run_id,
                                      self.pipeline_type,
                                      collection)
            msgbus.get_msg_bus().send_message(
                self.run_id,
                collection=collection,
                type=self.pipeline_type,
                custom_config=['pipeline.output_dir=%s' % output_dir,
                               'pipeline.is_operation=True',
                               'steps.clean.chain=1'])
        # Loop for endings
        while self.check_still_running():
            self.logger.debug("Just check for pipeline ending. Still working..")
            time.sleep(10)
        # Trigger publish
        msgbus.get_publish_bus().send_message(
            self.run_id,
            [x['collection'] for x in get_operation_db().get_run(self.run_id) if x['pipeline_status'] == 'SUCCESS']
        )



