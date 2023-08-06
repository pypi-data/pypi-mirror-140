
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
import subprocess
from cbpi.api import *
from cbpi.api.dataclasses import NotificationAction, NotificationType

logger = logging.getLogger(__name__)


@parameters([Property.Select(label="SocketNo", options=[1,2,3,4], description="Select the outlet of our socket")])
class GembirdActor(CBPiActor):

#    @action("Set Power", parameters=[Property.Number(label="Power", configurable=True,description="Power Setting [0-100]")])
#    async def setpower(self,Power = 100 ,**kwargs):
#        self.power=int(Power)
#        if self.power < 0:
#            self.power = 0
#        if self.power > 100:
#            self.power = 100
#        await self.set_power(self.power)

    def on_start(self):
        self.socket=self.props.get("SocketNo", None)
        self.state = False
        pass

    async def on(self, power=100):
        command = "sudo sispmctl -o {}".format(str(self.socket))
        try:
            subprocess.call(command, shell=True)
        except Exception as e:
            self.cbpi.notify("Gembird Actor Error", "Faied to switch socket. Please check configuration", NotificationType.ERROR)
            logging.error("Failed to switch Socket")
        self.state = True

    async def off(self):
        command = "sudo sispmctl -f {}".format(str(self.socket))
        try:
            subprocess.call(command, shell=True)
        except Exception as e:
            self.cbpi.notify("Gembird Actor Error", "Faied to switch socket. Please check configuration", NotificationType.ERROR)
            logging.error("Failed to switch Socket")

        self.state = False

    def get_state(self):
        return self.state
    
    async def run(self):
        pass

    async def set_power(self, power):
#        self.power = power
#        await self.cbpi.actor.actor_update(self.id,power)
        pass


def setup(cbpi):
    cbpi.plugin.register("Gembird USB Actor", GembirdActor)
    pass
