#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math

class Figure8Mission(Node):
    def __init__(self):
        super().__init__('figure8_mission')
        
        self.waypoints = self.generate_figure8_waypoints()
        self.current_waypoint = 0
        
        self.position_publisher = self.create_publisher(
            PoseStamped, '/drone/command/pose', 10
        )
        
        self.timer = self.create_timer(4.0, self.publish_next_waypoint)
        self.get_logger().info("Figure-8 Mission started!")
    
    def generate_figure8_waypoints(self, center_x=0, center_y=0, altitude=5, size=2.5, points=16):
        """Generate waypoints for a smooth figure-8 pattern"""
        waypoints = [(center_x, center_y, altitude)]  # Takeoff
        
        for i in range(points + 1):
            t = 2 * math.pi * i / points
            # Parametric equations for figure-8
            x = center_x + size * math.sin(t)
            y = center_y + size * math.sin(t) * math.cos(t)
            waypoints.append((x, y, altitude))
        
        waypoints.append((center_x, center_y, 0))  # Land
        return waypoints
    
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
            self.get_logger().info(f"Published waypoint {self.current_waypoint + 1}: ({x:.2f}, {y:.2f}, {z})")
            
            self.current_waypoint += 1
        else:
            self.get_logger().info("Figure-8 Mission completed!")
            self.timer.cancel()

def main(args=None):
    rclpy.init(args=args)
    mission = Figure8Mission()
    rclpy.spin(mission)
    mission.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
