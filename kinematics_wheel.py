import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import threading


class WheelControl(Node):
    def __init__(self):
        super().__init__('wheel_control')

        self.r = 0.03
        self.L = 0.17

        self.pub = self.create_publisher(
            Twist,
            '/model/vehicle_blue/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.control)

        self.left = 0.0
        self.right = 0.0

        self.start_time = time.time()
        self.is_running_motion = False
        self.duration = 15.0

    def set_wheel_speeds(self, left: float, right: float):
        """Memperbarui kecepatan roda dan mereset waktu awal berjalan."""
        self.left = left
        self.right = right
        self.start_time = time.time()
        self.is_running_motion = True

    def control(self):
        if not self.is_running_motion:
            return

        elapsed_time = time.time() - self.start_time
        msg = Twist()

        if elapsed_time < self.duration:
            v = - (self.r * (self.right + self.left) / 2.0)
            w = self.r * (self.right - self.left) / self.L

            msg.linear.x = v
            msg.angular.z = w
            self.pub.publish(msg)
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.pub.publish(msg)

            self.get_logger().info("15 detik berlalu. Robot berhenti.")
            self.is_running_motion = False


def input_thread(node: WheelControl, shutdown_event: threading.Event):
    """Loop input terminal yang terus berjalan tanpa henti."""
    print("\n==========================================")
    print("      PROGRAM KONTROL RODA ROS 2          ")
    print("==========================================")
    print("Ketik 'q' atau 'exit' kapan saja untuk keluar.\n")

    while not shutdown_event.is_set():
        try:
            val_left = input("\n[Input Baru] Roda kiri (rad/s)  : ").strip()
            if val_left.lower() in ['q', 'exit']:
                break

            val_right = input("[Input Baru] Roda kanan (rad/s) : ").strip()
            if val_right.lower() in ['q', 'exit']:
                break

            left_speed = float(val_left)
            right_speed = float(val_right)

            node.set_wheel_speeds(left_speed, right_speed)
            print(f">> Robot berjalan: Kiri = {left_speed} rad/s | Kanan = {right_speed} rad/s (selama 15 detik)")

        except ValueError:
            print("[!] Input tidak valid! Harap masukkan angka yang benar.")
        except (KeyboardInterrupt, EOFError):
            break

    shutdown_event.set()


def main():
    rclpy.init()
    node = WheelControl()

    shutdown_event = threading.Event()

    t = threading.Thread(target=input_thread, args=(node, shutdown_event), daemon=True)
    t.start()

    try:
        while rclpy.ok() and not shutdown_event.is_set():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.pub.publish(stop_msg)

        node.destroy_node()
        rclpy.shutdown()
        print("\nProgram telah dihentikan.")


if __name__ == '__main__':
    main()