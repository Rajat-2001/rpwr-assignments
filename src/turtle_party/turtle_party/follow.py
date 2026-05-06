import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import tf2_ros
import math

class FollowNode(Node):
    def __init__(self):
        super().__init__('follow')

        # ROS parameters — can be set from command line
        self.declare_parameter('target_frame', 'turtle1')
        self.declare_parameter('turtle_name', 'turtle2')

        self.target_frame = self.get_parameter('target_frame').get_parameter_value().string_value
        self.turtle_name = self.get_parameter('turtle_name').get_parameter_value().string_value

        self.get_logger().info(f"Following {self.target_frame} with {self.turtle_name}")

        # TF2 listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Publisher to move the follower turtle
        self.cmd_pub = self.create_publisher(
            Twist,
            f'/{self.turtle_name}/cmd_vel',
            10
        )

        # Timer — runs control loop at 10Hz
        self.timer = self.create_timer(0.1, self.control_loop)

    def control_loop(self):
        try:
            # Get transform from turtle_name to target_frame
            t = self.tf_buffer.lookup_transform(
                self.turtle_name,
                self.target_frame,
                rclpy.time.Time()
            )
        except Exception as e:
            self.get_logger().warn(f"TF not ready: {e}")
            return

        cmd = Twist()

        dx = t.transform.translation.x
        dy = t.transform.translation.y
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)

        # P-controller
        cmd.linear.x = 1.5 * distance
        cmd.angular.z = 4.0 * angle

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = FollowNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
