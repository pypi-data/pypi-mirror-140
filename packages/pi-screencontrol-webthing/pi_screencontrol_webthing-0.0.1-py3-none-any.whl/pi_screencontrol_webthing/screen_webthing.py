from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from pi_screencontrol_webthing.screen import Screen
from typing import List
import logging
import tornado.ioloop


class ScreenThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing


    def __init__(self, description: str):
        Thing.__init__(
            self,
            'urn:dev:ops:screen-1',
            'ScreenControl',
            ['MultiLevelSensor'],
            description
        )


        self.ioloop = tornado.ioloop.IOLoop.current()
        screen = Screen(self.on_log, self.on_activated)

        self.activated = Value(True, screen.show_display)
        self.add_property(
            Property(self,
                     'activated',
                     self.activated,
                     metadata={
                         '@type': 'OnOffProperty',
                         'title': 'Screen activated',
                         "type": "boolean",
                         'description': 'True, if the screen is activated',
                         'readOnly': False,
                     }))

        self.log = Value("")
        self.add_property(
            Property(self,
                     'log',
                     self.log,
                     metadata={
                         'title': 'Command log',
                         "type": "str",
                         'description': 'The executed commands',
                         'readOnly': True,
                     }))

        screen.update_timeout(3 * 60)


    def on_log(self, command_logs: List[str]):
        self.ioloop.add_callback(self.__update_log, command_logs)

    def __update_log(self, command_logs: List[str]):
        self.log.notify_of_external_update("\n".join(command_logs))

    def on_activated(self, is_on: bool):
        self.ioloop.add_callback(self.__update_activated, is_on)

    def __update_activated(self, is_on: bool):
        self.activated.notify_of_external_update(is_on)


def run_server(port: int, description: str):
    screenThing = ScreenThing(description)
    server = WebThingServer(SingleThing(screenThing), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')
