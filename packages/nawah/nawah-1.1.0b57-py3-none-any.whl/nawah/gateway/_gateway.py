import asyncio
import logging
import traceback

from nawah.classes import InvalidGatewayException, UnexpectedGatewayException
from nawah.config import Config

logger = logging.getLogger('nawah')


class Gateway:
    @staticmethod
    def send(*, gateway: str, **kwargs):
        if Config.test:
            logger.debug('Skipping \'Gateway.send\' action due to test mode.')
            return

        if gateway not in Config.gateways.keys():
            raise InvalidGatewayException(gateway=gateway)

        try:
            gateway_call = Config.gateways[gateway](**kwargs)
            if asyncio.iscoroutine(gateway_call):
                asyncio.create_task(gateway_call)
        except Exception:
            logger.error('Gateway call with following \'kwargs\' failed:')
            logger.error(kwargs)
            logger.error(traceback.format_exc())
            raise UnexpectedGatewayException(gateway=gateway)

        return
