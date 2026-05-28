#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscriber = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.twist = Twist()
        self.front_dist = 10.0
        self.right_dist = 10.0
        self.target_dist = 0.5  # We want to stay 0.5 meters from the wall

    def get_min_distance(self, ranges):
        """Helper to filter out infinity/NaN errors from the laser sensor"""
        valid_ranges = [r for r in ranges if not math.isinf(r) and not math.isnan(r) and r > 0.0]
        return min(valid_ranges) if valid_ranges else 10.0

    def scan_callback(self, msg):
        ranges = msg.ranges
        num_ranges = len(ranges)
        
        if num_ranges > 0:
            # Front of the robot (0 degrees)
            front_slice = ranges[0:20] + ranges[-20:]
            self.front_dist = self.get_min_distance(front_slice)
            
            # Right side of the robot (approx 270 degrees)
            right_idx = int(num_ranges * 0.75)
            right_slice = ranges[right_idx-20:right_idx+20]
            self.right_dist = self.get_min_distance(right_slice)

    def control_loop(self):
        if self.front_dist < 0.6:
            # Corner detected! Spin left to avoid hitting the wall
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.5
            self.get_logger().info('Corner ahead! Turning left...')
            
        elif self.right_dist > 1.5:
            # SEARCH MODE: No wall nearby. Drive straight until we find one!
            self.twist.linear.x = 0.3
            self.twist.angular.z = 0.0
            self.get_logger().info('Searching for a wall...')
            
        elif self.right_dist < (self.target_dist - 0.1):
            # Too close to the right wall, veer slightly left
            self.twist.linear.x = 0.2
            self.twist.angular.z = 0.2
            self.get_logger().info('Too close! Veering left...')
            
        elif self.right_dist > (self.target_dist + 0.1):
            # Too far from the right wall, veer slightly right
            self.twist.linear.x = 0.2
            self.twist.angular.z = -0.2
            self.get_logger().info('Too far! Veering right...')
            
        else:
            # Perfect distance, drive straight ahead
            self.twist.linear.x = 0.3
            self.twist.angular.z = 0.0
            self.get_logger().info('Perfect distance. Cruising...')
            
        self.publisher.publish(self.twist)

def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
