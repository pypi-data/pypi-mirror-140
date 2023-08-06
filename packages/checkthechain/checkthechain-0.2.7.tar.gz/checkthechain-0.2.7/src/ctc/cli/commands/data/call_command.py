from ctc import rpc


def get_command_spec():
    return {
        'f': async_call_command,
        'help': 'output result of a call',
        'args': [
            {'name': 'to_address'},
            {'name': 'function_name'},
            {'name': 'args', 'nargs': '*'},
            {'name': '--quiet', 'action': 'store_true'},
        ],
    }


async def async_call_command(to_address, function_name, args, quiet):

    if not quiet:
        print('performing eth_call')
        print('- to address:', to_address)
        print('- function:', function_name)
        print('- arguments:', args)
        print()
        print('result:')

    result = await rpc.async_eth_call(
        to_address=to_address,
        function_name=function_name,
        function_parameters=args,
    )
    print(result)

    await rpc.async_close_http_session()

