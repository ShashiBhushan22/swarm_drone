#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class BoxMission(Node):
    def __init__(self):
        super().__init__('box_mission')
        
        # Generate box waypoints
        self.waypoints = self.generate_box_waypoints()
        self.current_waypoint = 0
        
        # Publisher to send commands to the existing controller
        self.position_publisher = self.create_publisher(
            PoseStamped, 
            '/drone/command/pose', 
            10
        )
        
        # Timer to publish waypoints sequentially
        self.timer = self.create_timer(5.0, self.publish_next_waypoint)  # 5 second interval
        
        self.get_logger().info("Box Mission started!")
        self.get_logger().info(f"Total waypoints: {len(self.waypoints)}")
    
    def generate_box_waypoints(self, center_x=0, center_y=0, altitude=5, size=3):
        """Generate waypoints for a box pattern"""
        half_size = size / 2
        return [
            (center_x, center_y, altitude),          # Takeoff
            (center_x + half_size, center_y, altitude),          # Point 1
            (center_x + half_size, center_y + half_size, altitude),  # Point 2
            (center_x, center_y + half_size, altitude),          # Point 3
            (center_x - half_size, center_y + half_size, altitude),  # Point 4
            (center_x - half_size, center_y, altitude),          # Point 5
            (center_x, center_y, altitude),          # Return to center
            (center_x, center_y, 0)                  # Land
        ]
    
    def publish_next_waypoint(self):
        if self.current_waypoint < len(self.waypoints):
            x, y, z = self.waypoints[self.current_waypoint]
            
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "map"
            msg.pose.position.x = float(x)
            msg.pose.position.y = float(y)
            msg.pose.position.z = float(z)
            msg.pose.orientation.w = 1.0
            
            self.position_publisher.publish(msg)
            self.get_logger().info(f"Published waypoint {self.current_waypoint + 1}: ({x}, {y}, {z})")
            
            self.current_waypoint += 1
        else:
            self.get_logger().info("Box Mission completed!")
            self.timer.cancel()

def main(args=None):
    rclpy.init(args=args)
    box_mission = BoxMission()
    rclpy.spin(box_mission)
    box_mission.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
