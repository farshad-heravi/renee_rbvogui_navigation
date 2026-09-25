'''
The code developed by Farshad Nozad Heravi (fnh) for the Renee project.
Email: f.n.heravi@gmail.com
GitHub: https://github.com/farshad-heravi

Switch which lasers feed the real-robot collision_monitor
(config/collision_monitor_real.yaml) at runtime:

    ros2 run renee_rbvogui_navigation collision_mode both|front|rear|none

A mode is only the *.enabled flags of each laser's Stop/Slow polygons and its
scan source. nav2_task.launch.py imports mode_parameters() to set the initial
mode, so launch-time and runtime switching share this one table. A small
rclpy client instead of `ros2 param set`, which hangs in this setup.
'''

import sys

import rclpy
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters

# mode -> (front laser used, rear laser used)
MODES = {
    'both': (True, True),
    'front': (True, False),
    'rear': (False, True),
    'none': (False, False),
}

_LASER_PARAMS = {
    'front': ['FrontStop.enabled', 'FrontSlow.enabled', 'front_scan.enabled'],
    'rear': ['RearStop.enabled', 'RearSlow.enabled', 'rear_scan.enabled'],
}


def mode_parameters(mode):
    '''Return the {param_name: bool} overrides for a collision mode.'''
    if mode not in MODES:
        raise ValueError(
            f"Unknown collision mode '{mode}', expected one of {list(MODES)}")
    front, rear = MODES[mode]
    params = {name: front for name in _LASER_PARAMS['front']}
    params.update({name: rear for name in _LASER_PARAMS['rear']})
    return params


def main():
    args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    if len(args) < 1 or args[0] not in MODES:
        print(f"usage: collision_mode {{{'|'.join(MODES)}}} [node_name]")
        sys.exit(2)
    mode = args[0]
    node_name = args[1] if len(args) > 1 else '/robot/collision_monitor'

    rclpy.init()
    node = rclpy.create_node('collision_mode_client')
    client = node.create_client(SetParameters, f'{node_name}/set_parameters')
    if not client.wait_for_service(timeout_sec=5.0):
        print(f'{node_name}/set_parameters not available — is navigation-real up?')
        sys.exit(1)

    request = SetParameters.Request()
    request.parameters = [
        Parameter(name=name, value=ParameterValue(
            type=ParameterType.PARAMETER_BOOL, bool_value=value))
        for name, value in mode_parameters(mode).items()
    ]
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    if future.result() is None:
        print('set_parameters call timed out')
        sys.exit(1)

    ok = True
    for param, result in zip(request.parameters, future.result().results):
        if not result.successful:
            ok = False
            print(f'  {param.name}: rejected ({result.reason})')
    print(f"collision mode -> {mode}" if ok else 'collision mode only partially applied')
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
