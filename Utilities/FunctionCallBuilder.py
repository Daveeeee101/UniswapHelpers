import json
from typing import Dict, Tuple, List
from eth_abi.exceptions import InsufficientDataBytes
from Web3Types.SimpleTypes import *
from web3 import Web3
from eth_abi import encode, decode
from Definitions import ROOT_DIR

ABI_FILENAME = ROOT_DIR + '/Files/abi.json'


class BadFunctionCall(Exception):
    pass


def get_abi(contract_type: str) -> Dict:
    with open(ABI_FILENAME) as abi:
        json_object = json.loads(abi.read())[contract_type]
        return json_object


def get_function_from_abi(abi: Dict, function_name: str, input_params=None):
    function = None
    for f in abi:
        if f['type'] == 'function':
            if f['name'] == function_name:
                if input_params is not None:
                    if len(f['inputs']) == input_params:
                        function = f
                else:
                    function = f
    if function is None:
        raise BadFunctionCall("Couldn't find correct function")
    return function


def create_function_call_abi(abi: Dict, function_name: str) -> HexBytes:
    function = get_function_from_abi(abi, function_name)
    return create_function_call(function)


def get_abi_function(function_name: str, contract_type: str) -> Dict:
    with open(ABI_FILENAME) as abi:
        json_object = json.loads(abi.read())[contract_type]
        return get_function_from_abi(json_object, function_name)


def create_function_ident(abi: Dict, function_name: str, input_length=None) -> HexBytes:
    if input_length is None:
        function = get_function_from_abi(abi, function_name)
    else:
        function = get_function_from_abi(abi, function_name, input_length)
    arguments = "("
    for i in function['inputs'][:-1]:
        arg_type = i['type']
        arguments += arg_type
        arguments += ","
    if len(function['inputs']) > 0:
        arguments += function['inputs'][-1]['type']
    arguments += ")"
    function_prototype = function['name'] + arguments
    return HexBytes(bytes(Web3.keccak(text=function_prototype))[:4])


def pad_val(value: str, positive: bool):
    if not positive:
        while len(value) != 64:
            value = "ff" + value
        return value
    else:
        while len(value) != 64:
            value = "00" + value
        return value


def create_function_call(abi_function: Dict, *args) -> HexBytes:
    function = abi_function
    arguments = "("
    if len(args) != len(function['inputs']):
        raise BadFunctionCall("Incorrect number of arguments")
    """if function['inputs'][0]['type'] == "int16":
        val = encode_packed(["int16"], [args[0]]).hex()
        encoded_args = pad_val(val, False)
    else:"""
    encoded_args = encode([i['type'] for i in function['inputs']], [str(a) if type(a) == Address else bytes(a) if type(a) == HexBytes else a for a in args]).hex()
    for i in function['inputs'][:-1]:
        arg_type = i['type']
        arguments += arg_type
        arguments += ","
    if len(function['inputs']) > 0:
        arguments += function['inputs'][-1]['type']
    arguments += ")"
    function_prototype = function['name'] + arguments
    function_selector = Web3.keccak(text=function_prototype).hex()[:10]
    return HexBytes(function_selector + encoded_args)


def create_event_abi(event_name: str, contract_abi: Dict):
    event = None
    for f in contract_abi:
        if f['type'] == 'event':
            if f['name'] == event_name:
                event = f
    if event is None:
        raise BadFunctionCall("Couldn't find correct function")
    return event


def create_event_topic(event_abi):
    arguments = "("
    for i in event_abi['inputs'][:-1]:
        arg_type = i['type']
        arguments += arg_type
        arguments += ","
    if len(event_abi['inputs']) > 0:
        arguments += event_abi['inputs'][-1]['type']
    arguments += ")"
    function_prototype = event_abi['name'] + arguments
    return HexBytes(bytes(Web3.keccak(text=function_prototype)))


def decode_event_output(output: HexBytes, event_abi: Dict) -> Tuple:
    function_abi_outputs = event_abi['inputs']
    types = [f['type'] for f in function_abi_outputs if f['indexed'] == False]
    outs = decode(types, bytes(output))
    outs = tuple(Address(o) if t == "address" else ([Address(q) for q in o] if t == "address[]" else (list(o) if t[-2:] == "[]" else o)) for t, o in zip(types, outs))
    return outs


def decode_topic_data(topics: List[HexBytes], event_abi: Dict) -> List:
    indexed_function_output_types = [f['type'] for f in event_abi['inputs'] if f['indexed']]
    outs = [decode([typ], bytes(val))[0] for typ, val in zip(indexed_function_output_types, topics[1:])]
    outs = list(Address(o) if t == "address" else (
        [Address(q) for q in o] if t == "address[]" else (list(o) if t[-2:] == "[]" else o)) for t, o in
                 zip(indexed_function_output_types, outs))
    return outs


def decode_function_output(output: HexBytes, function_abi: Dict) -> Tuple:
    function_abi_outputs = function_abi['outputs']
    types = [f['type'] for f in function_abi_outputs]
    try:
        outs = decode(types,  bytes(output))
        outs = tuple(Address(o) if t == "address" else ([Address(q) for q in o] if t == "address[]" else (list(o) if t[-2:] == "[]" else o)) for t, o in zip(types, outs))
        return outs
    except (OverflowError, InsufficientDataBytes):
        return None


def decode_function_input_abi(input_data: HexBytes, function_name, contract_abi, input_length=None) -> Tuple:
    function = get_function_from_abi(contract_abi, function_name, input_params=input_length)
    types = [f['type'] for f in function['inputs']]
    outs = decode(types, bytes(input_data))
    outs = tuple(Address(o) if t == "address" else ([Address(q) for q in o] if t == "address[]" else (list(o) if t[-2:] == "[]" else o)) for t, o in zip(types, outs))
    return outs


def decode_function_input_abi_with_names(input_data: HexBytes, function_name, contract_abi, input_length=None) -> Dict:
    function = get_function_from_abi(contract_abi, function_name, input_params=input_length)
    types = [f['type'] for f in function['inputs']]
    outs = decode(types, bytes(input_data))
    outs = tuple(Address(o) if t == "address" else ([Address(q) for q in o] if t == "address[]" else (list(o) if t[-2:] == "[]" else o)) for t, o in zip(types, outs))
    outs = {name["name"]: value for name, value in zip(function['inputs'], outs)}
    return outs


def decode_router_transaction_input(data: HexBytes):
    router_abi = get_abi('router')
    codes = {
        create_function_ident(router_abi, 'swapETHForExactTokens'): "swapETHForExactTokens",
        create_function_ident(router_abi, 'swapExactETHForTokens'): "swapExactETHForTokens",
        create_function_ident(router_abi, 'swapExactTokensForETH'): "swapExactTokensForETH",
        create_function_ident(router_abi, 'swapTokensForExactETH'): "swapTokensForExactETH",
        create_function_ident(router_abi, 'swapExactTokensForTokens'): "swapExactTokensForTokens",
        create_function_ident(router_abi, 'swapTokensForExactTokens'): "swapTokensForExactTokens"
    }
    try:
        function_name = codes[data[:4]]
    except KeyError:
        return None, None
    function_input = data[4:]
    decoded = decode_function_input_abi(function_input, function_name, router_abi)
    return function_name, decoded


def decode_universal_router_transaction_input(data: HexBytes):
    router_abi = get_abi('universalRouter')
    codes = {
        create_function_ident(router_abi, 'execute', 3): "execute_deadline",
        create_function_ident(router_abi, 'execute', 2): "execute_no_deadline"
    }
    router_commands = {
        8: "V2_SWAP_EXACT_IN",
        9: "V2_SWAP_EXACT_OUT"
    }
    try:
        function_name = codes[data[:4]]
    except KeyError:
        return None, None
    function_input = data[4:]
    if function_name == "execute_deadline":
        commands, inputs, deadline = decode_function_input_abi(function_input, 'execute', router_abi, 3)
        sep_commands = [int(x) for x in commands]
        for i, s in zip(inputs, sep_commands):
            if s in router_commands:
                recipient, amountIn, amountOutMin, path, payerIsUser = decode(["address", "uint256", "uint256", "address[]", "bool"], i)
                print(recipient, amountIn, amountOutMin, path, payerIsUser)
                return function_name, router_commands[s], (recipient, amountIn, amountOutMin, [Address(s)for s in path], payerIsUser, deadline)
    else:
        commands, inputs = decode_function_input_abi(function_input, 'execute', router_abi, 2)
        sep_commands = [int(x) for x in commands]
        for i, s in zip(inputs, sep_commands):
            if s in router_commands.values():
                recipient, amountIn, amountOutMin, path, payerIsUser = decode(
                    ["address", "uint256", "uint256", "address[]", "bool"], i)
                print(recipient, amountIn, amountOutMin, path, payerIsUser)
                return function_name, router_commands[s], (recipient, amountIn, amountOutMin, [Address(s) for s in path], payerIsUser)


if __name__ == '__main__':
    print(decode(b"0x111111111111111111111111111111111111111111111111111111111111111111"), "")
