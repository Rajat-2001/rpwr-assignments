from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, ExecuteProcess

def generate_launch_description():
    return LaunchDescription([

        # Start turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),

        # Broadcast turtle1 TF
        Node(
            package='turtle_tf2_py',
            executable='turtle_tf2_broadcaster',
            name='broadcaster1',
            parameters=[{'turtlename': 'turtle1'}]
        ),

        # Spawn turtle2 via service call after 2 seconds
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn',
                         'turtlesim/srv/Spawn',
                         '{x: 2.0, y: 2.0, theta: 0.0, name: "turtle2"}'],
                    output='screen'
                )
            ]
        ),

        # Broadcast turtle2 TF after spawn
        TimerAction(
            period=6.0,
            actions=[
                Node(
                    package='turtle_tf2_py',
                    executable='turtle_tf2_broadcaster',
                    name='broadcaster2',
                    parameters=[{'turtlename': 'turtle2'}]
                ),
            ]
        ),

        # Start follow node after everything is ready
        TimerAction(
            period=8.0,
            actions=[
                Node(
                    package='turtle_party',
                    executable='follow',
                    name='follow',
                    parameters=[
                        {'target_frame': 'turtle1'},
                        {'turtle_name': 'turtle2'}
                    ]
                ),
            ]
        ),

    ])
