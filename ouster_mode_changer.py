import socket
import rospy
from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse

class OusterModeChanger:
    def __init__(self):
        self.IP = '172.16.0.2'
        self.PORT = 7501
        self.COMMAND_GET_OPERATING_MODE = "get_config_param active operating_mode\n"
        self.COMMAND_SET_OPERATING_MODE_NORMAL = "set_config_param operating_mode NORMAL\n"
        self.COMMAND_SET_OPERATING_MODE_STANDBY = "set_config_param operating_mode STANDBY\n"
        self.COMMAND_REINITIALIZE = "reinitialize\n"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.IP, self.PORT))
        self.service = rospy.Service('ouster_mode', SetBool, self.service_callback)
        self.cnt = 0
        self.retries = 5

    def send(self, command):
            self.sock.send(command.encode())
            print(f"send: {command}")
            result = self.sock.recv(1024)
            recv_result = result.decode()
            print(f"recv: {recv_result}")
            return recv_result

    def change_mode_normal(self):
        if self.send(self.COMMAND_GET_OPERATING_MODE) != "\"NORMAL\"\n":
            self.cnt = 0
            while self.send(self.COMMAND_SET_OPERATING_MODE_NORMAL) != "set_config_param\n":
                self.cnt += 1
                if self.cnt > self.retries:
                    print("Failed to set NORMAL mode")
                    return False
            self.cnt = 0
            while self.send(self.COMMAND_REINITIALIZE) != "reinitialize\n":
                self.cnt += 1
                if self.cnt > self.retries:
                    print("Failed to reinitialize")
                    return False
            return True
        return True

    def change_mode_standby(self):
        if self.send(self.COMMAND_GET_OPERATING_MODE) != "\"STANDBY\"\n":
            self.cnt = 0
            while self.send(self.COMMAND_SET_OPERATING_MODE_STANDBY) != "set_config_param\n":
                self.cnt += 1
                if self.cnt > self.retries:
                    print("Failed to set STANDBY mode")
                    return False
            self.cnt = 0
            while self.send(self.COMMAND_REINITIALIZE) != "reinitialize\n":
                self.cnt += 1
                if self.cnt > self.retries:
                    print("Failed to reinitialize")
                    return False
            return True
        return True

    def service_callback(self, request):
        response = SetBoolResponse()
        if request.data:
            response.success = self.change_mode_normal()
        else:
            response.success = self.change_mode_standby()
        
        return response
        
    def __del__(self):
        self.sock.close()

if __name__ == '__main__':
    rospy.init_node("ouster_mode_change_node")
    ouster_mode_changer = OusterModeChanger()
    rospy.spin()
