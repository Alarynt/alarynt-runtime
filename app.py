import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from RestrictedPython import compile_restricted, safe_globals
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Hardcoded timeout for execution (in seconds)
EXECUTION_TIMEOUT = 1

def lambda_handler(event, context):
    """
    Main Lambda entry point.
    Accepts an event payload and evaluates it against user-defined logic.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # 1. Get rule logic (example: from event payload)
    try:
        user_code = event['rule_logic']
        event_payload = event['payload']
    except KeyError as e:
        logger.error(f"Missing key in event: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {e}'})
        }

    # 2. Prepare the sandboxed environment
    # Only expose safe built-ins and variables
    safe_locals = {'event': event_payload}
    
    # Use a ThreadPoolExecutor to enforce a timeout
    with ThreadPoolExecutor(max_workers=1) as executor:
        start_time = time.time()
        future = executor.submit(sandboxed_eval, user_code, safe_globals, safe_locals)
        try:
            # 3. Execute with a timeout
            result = future.result(timeout=EXECUTION_TIMEOUT)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            logger.info(f"Execution result: {result} in {execution_time_ms:.2f}ms")
            
            # 4. Return the result
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'matched': bool(result),
                    'result': result,
                    'trace': {
                        'execution_time_ms': execution_time_ms
                    }
                })
            }

        except TimeoutError:
            logger.warning("Execution timed out")
            return {
                'statusCode': 408,
                'body': json.dumps({'error': 'Execution timed out'})
            }
        except Exception as e:
            logger.error(f"An error occurred during execution: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

def sandboxed_eval(code, s_globals, s_locals):
    """
    Compiles and executes the user code in a restricted environment.
    The user code is expected to assign its output to a 'result' variable.
    """
    byte_code = compile_restricted(code, '<string>', 'exec')
    
    # The result of the evaluated expression is returned
    exec(byte_code, s_globals, s_locals)
    return s_locals.get('result') 