#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from px4_msgs.msg import TrajectorySetpoint, OffboardControlMode, VehicleCommand
import math
import time

class SpiralMission(Node):
    def __init__(self):
        super().__init__('spiral_mission')
        
        # Publishers to PX4 (same as the existing controller)
        self.trajectory_publisher = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        
        self.offboard_publisher = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        
        self.vehicle_command_publisher = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        self.waypoints = self.generate_spiral_waypoints()
        self.current_waypoint = 0
        
        # Set up offboard control and arm the drone
        self.offboard_setpoint_counter = 0
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info("Spiral Mission started!")
    
    def generate_spiral_waypoints(self, center_x=0, center_y=0, max_radius=4, max_altitude=8, turns=2):
        """Generate waypoints for an ascending spiral pattern"""
        waypoints = [(center_x, center_y, 3)]  # Takeoff to 3m
        
        points_per_turn = 12
        total_points = turns * points_per_turn
        
        for i in range(total_points + 1):
            angle = 2 * math.pi * i / points_per_turn
            radius = max_radius * (i / total_points)
            altitude = 3 + (max_altitude - 3) * (i / total_points)
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            waypoints.append((x, y, altitude))
        
        waypoints.append((center_x, center_y, max_altitude))
        waypoints.append((center_x, center_y, 0))
        return waypoints
    
    def timer_callback(self):
        # Publish offboard control mode
        offboard_msg = OffboardControlMode()
        offboard_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        offboard_msg.position = True
        offboard_msg.velocity = False
        offboard_msg.acceleration = False
        offboard_msg.attitude = False
        offboard_msg.body_rate = False
        self.offboard_publisher.publish(offboard_msg)
        
        # Arm and set offboard mode in the first few iterations
        if self.offboard_setpoint_counter < 10:
            self.offboard_setpoint_counter += 1
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1., 6.)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            return
        
        # Publish waypoints
        if self.current_waypoint < len(self.waypoints):
            x, y, z = self.waypoints[self.current_waypoint]
            
            trajectory_msg = TrajectorySetpoint()
            trajectory_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
            
            # CORRECTED: Use only the fields that exist in the message
            trajectory_msg.position = [float(x), float(y), -float(z)]  # NED frame (negative Z = up)
            trajectory_msg.yaw = 0.0
            trajectory_msg.yawspeed = 0.0
            # velocity, acceleration, and jerk are optional - only set if needed
            # trajectory_msg.velocity = [0.0, 0.0, 0.0]
            # trajectory_msg.acceleration = [0.0, 0.0, 0.0]
            # trajectory_msg.jerk = [0.0, 0.0, 0.0]
            
            self.trajectory_publisher.publish(trajectory_msg)
            self.get_logger().info(f"Published to PX4: ({x:.2f}, {y:.2f}, {z:.2f})")
            
            self.current_waypoint += 1
        else:
            self.get_logger().info("Spiral Mission completed! Landing...")
            self.timer.cancel()
    
    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        """Publish vehicle commands"""
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    mission = SpiralMission()
    rclpy.spin(mission)
    mission.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
