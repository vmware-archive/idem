# Import python libs
import yaml


async def render(hub, data):
    return yaml.safe_load(data)
