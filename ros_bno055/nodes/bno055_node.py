#!/usr/bin/env python
from __future__ import print_function, division

import sys
import rospy
import math
import time
import serial

from std_msgs.msg import Header
from sensor_msgs.msg import Imu


class BNO055Driver(object):

    def __init__(self):
        serial_port = rospy.get_param('~serial_port', '/dev/ttyACM0')

        try:
            self.device = self.serial_connection(serial_port=serial_port,serial_timeout_sec=5)
        except:
            rospy.logerr('unable to find IMU at port {}'.format(serial_port))
            sys.exit(-1)

        self.imu_pub = rospy.Publisher('imu/data', Imu, queue_size=1)
        self.frame_id = rospy.get_param('~frame_id', '/base_imu')
        self.seq = 0
        self.reset_msgs()
    def serial_connection(self,serial_port=None,serial_timeout_sec=5):
	if serial_port is not None:
            # Use serial communication if serial_port name is provided.
            # Open the serial port at 115200 baud, 8N1.  Add a 5 second timeout
            # to prevent hanging if device is disconnected.
	    print (serial_port)
            self._serial = serial.Serial(serial_port, 9600, timeout=serial_timeout_sec,
                                         writeTimeout=serial_timeout_sec)
	return self._serial
    def parse_serial(self):
	data=self.device.readline()
	#print (data)
	
	try:
	#	AX,AY,AZ,GX,GY,GZ,QX,QY,QZ,QW=data.split(":")
		AA=data.split(":")
		#print (AA, len(AA))
		if (len(AA) == 10):
			return AA
		else:
			return None
	except:
		print ("PARSE HATA")
		return None
	
    def reset_msgs(self):
        self.imu_msg = Imu()

        # ignore the covariance data
        self.imu_msg.orientation_covariance[0] = -1
        self.imu_msg.angular_velocity_covariance[0] = -1
        self.imu_msg.linear_acceleration_covariance[0] = -1


    def publish_data(self):
        h = Header()
        h.stamp = rospy.Time.now()
        h.frame_id = self.frame_id
        h.seq = self.seq
        self.seq = self.seq + 1

        self.imu_msg.header = h
	data=self.parse_serial()
	if data is not None:
		datas=data
		#print (datas[9])
        #q = self.device.read_quaternion()
		self.imu_msg.orientation.x = float(datas[6])
		self.imu_msg.orientation.y = float(datas[7])
		self.imu_msg.orientation.z = float(datas[8])
		self.imu_msg.orientation.w = float(datas[9])

		#g = self.device.read_gyroscope()
		# convert from deg/sec to rad/sec
		self.imu_msg.angular_velocity.x = float(datas[3]) * math.pi / 180.0
		self.imu_msg.angular_velocity.y = float(datas[4]) * math.pi / 180.0
		self.imu_msg.angular_velocity.z = float(datas[5]) * math.pi / 180.0

		#a = self.device.read_linear_acceleration()
		self.imu_msg.linear_acceleration.x = float(datas[0])
		self.imu_msg.linear_acceleration.y = float(datas[1])
		self.imu_msg.linear_acceleration.z = float(datas[2])
		self.imu_pub.publish(self.imu_msg)

		
	

def main():
    rospy.init_node('bno055_driver')
    node = BNO055Driver()
    while not rospy.is_shutdown():
        node.publish_data()
	#node.parse_serial()

if __name__ == '__main__':
    main()
