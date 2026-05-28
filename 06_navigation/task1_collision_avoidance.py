#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, qos_profile_sensor_data
import math

class CollisionAvoidance(Node):
    def __init__(self):
        super().__init__('collision_avoidance')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel_unstamped', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data
        )
        
        self.safe_distance = 0.6  # meters
        self.cmd = Twist()
        self.get_logger().info("Collision Avoidance Node Started.")

    def scan_callback(self, msg):
        # The laser scan usually has 0 degrees at the front (index 0)
        # We check a window of +/- 15 degrees in the front
        front_ranges = msg.ranges[-15:] + msg.ranges[:15]
        
        # Filter out inf and nan values
        valid_ranges = [r for r in front_ranges if not math.isinf(r) and not math.isnan(r) and r > msg.range_min]
        
        min_front_distance = min(valid_ranges) if valid_ranges else float('inf')

        if min_front_distance < self.safe_distance:
            # Obstacle detected: Turn on the spot
            self.cmd.linear.x = 0.0
            self.cmd.angular.z = 0.5  # Turn left
            self.get_logger().info(f"Obstacle at {min_front_distance:.2f}m! Turning...")
        else:
            # Path clear: Move forward
            self.cmd.linear.x = 0.3
            self.cmd.angular.z = 0.0
            
        self.publisher_.publish(self.cmd)

def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd.linear.x = 0.0
        node.cmd.angular.z = 0.0
        node.publisher_.publish(node.cmd)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
