#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class WheelController(Node):

    def __init__(self):
        super().__init__('wheel_controller')

        self.radius_roda = 0.05
        self.jarak_roda = 0.50

        self.velocity_sub = self.create_subscription(
            Twist,
            '/input_ik',
            self.calculate_velocity,
            10
        )

        self.pub_kiri = self.create_publisher(
            Float64,
            '/left_wheel/command',
            10
        )

        self.pub_kanan = self.create_publisher(
            Float64,
            '/right_wheel/command',
            10
        )

        self.gazebo_pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.get_logger().info(
            'Wheel Controller dengan inverse kinematics aktif.'
        )

    def calculate_velocity(self, data):

        vx = data.linear.x
        wz = data.angular.z

        wheel_left = (
            vx - (self.jarak_roda * 0.5) * wz
        ) / self.radius_roda

        wheel_right = (
            vx + (self.jarak_roda * 0.5) * wz
        ) / self.radius_roda

        command_left = Float64()
        command_right = Float64()

        command_left.data = float(wheel_left)
        command_right.data = float(wheel_right)

        self.pub_kiri.publish(command_left)
        self.pub_kanan.publish(command_right)

        gazebo_command = Twist()

        gazebo_command.linear.x = (
            self.radius_roda / 2.0
        ) * (wheel_left + wheel_right)

        gazebo_command.angular.z = (
            self.radius_roda / self.jarak_roda
        ) * (wheel_right - wheel_left)

        self.gazebo_pub.publish(gazebo_command)

        self.get_logger().info(
            f'Vx = {vx:.3f} m/s | '
            f'Wz = {wz:.3f} rad/s | '
            f'Kiri = {wheel_left:.3f} rad/s | '
            f'Kanan = {wheel_right:.3f} rad/s'
        )

    def stop_robot(self):

        left_stop = Float64()
        right_stop = Float64()

        left_stop.data = 0.0
        right_stop.data = 0.0

        self.pub_kiri.publish(left_stop)
        self.pub_kanan.publish(right_stop)

        stop_command = Twist()

        stop_command.linear.x = 0.0
        stop_command.angular.z = 0.0

        self.gazebo_pub.publish(stop_command)


def main(args=None):

    rclpy.init(args=args)

    controller = WheelController()

    try:
        rclpy.spin(controller)

    except KeyboardInterrupt:
        controller.get_logger().info(
            'Wheel Controller dihentikan.'
        )

    finally:
        controller.stop_robot()
        controller.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()