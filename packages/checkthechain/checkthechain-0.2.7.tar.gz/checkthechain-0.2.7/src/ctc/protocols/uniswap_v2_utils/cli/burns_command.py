from ctc.protocols import uniswap_v2_utils

from ctc.cli import cli_utils
from ctc import rpc


def get_command_spec():
    return {
        'f': async_burns_command,
        'help': 'output information about pool burns',
        'args': [
            {'name': 'pool'},
            {'name': '--blocks', 'nargs': '+'},
            {'name': '--output'},
            {'name': '--overwrite', 'action': 'store_true'},
        ],
    }


async def async_burns_command(pool, blocks, output, overwrite):

    if blocks is not None:
        start_block, end_block = await cli_utils.async_resolve_block_range(blocks)
    else:
        start_block = None
        end_block = None

    burns = await uniswap_v2_utils.async_get_pool_burns(
        pool,
        start_block=start_block,
        end_block=end_block,
    )
    cli_utils.output_data(burns, output, overwrite)

    await rpc.async_close_http_session()

