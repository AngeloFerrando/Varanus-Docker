#!/usr/bin/env python3
import rospy
import sys
import json
import yaml
import websocket
from threading import *
from rospy_message_converter import message_converter
from monitor.msg import *
from std_msgs.msg import *

from gazebo_radiation_plugins.msg import Command
from std_msgs.msg import Int16
from gazebo_radiation_plugins.msg import Inspection
from gazebo_radiation_plugins.msg import Simulated_Radiation_Msg

ws_lock = RLock()
dict_msgs = {}
pub_dict = {}
srv_type_dict = dict()
topics_to_republish = []
msg_dict = { '/radiation_sensor_plugin/sensor_0' : "gazebo_radiation_plugins/Simulated_Radiation_Msg",  '/command' : "gazebo_radiation_plugins/Command",  '/inspected' : "gazebo_radiation_plugins/Inspection",  '/currentLoc' : "std_msgs/Int16"}

def callback__radiation_sensor_plugin_sensor_0(data):
	global ws, ws_lock
	d = message_converter.convert_ros_message_to_dictionary(data)
	d['topic'] = '/radiation_sensor_plugin/sensor_0' 
	rospy.loginfo('monitor has observed the following message on topic '+d['topic']+ ":\n" + str(data))
	d['time'] = rospy.get_time()
	ws_lock.acquire()
	while d['time'] in dict_msgs:
		d['time'] += 0.01
	ws.send(json.dumps(d))
	dict_msgs[d['time']] = data
	msg = ws.recv()
	ws_lock.release()

	return on_message_topic(msg)

def callback__command(data):
	global ws, ws_lock
	d = message_converter.convert_ros_message_to_dictionary(data)
	d['topic'] = '/command' 
	rospy.loginfo('monitor has observed the following message on topic '+d['topic']+ ":\n" + str(data))
	d['time'] = rospy.get_time()
	ws_lock.acquire()
	while d['time'] in dict_msgs:
		d['time'] += 0.01
	ws.send(json.dumps(d))
	dict_msgs[d['time']] = data
	msg = ws.recv()
	ws_lock.release()

	return on_message_topic(msg)

def callback__inspected(data):
	global ws, ws_lock
	d = message_converter.convert_ros_message_to_dictionary(data)
	d['topic'] = '/inspected' 
	rospy.loginfo('monitor has observed the following message on topic '+d['topic']+ ":\n" + str(data))
	d['time'] = rospy.get_time()
	ws_lock.acquire()
	while d['time'] in dict_msgs:
		d['time'] += 0.01
	ws.send(json.dumps(d))
	dict_msgs[d['time']] = data
	msg = ws.recv()
	ws_lock.release()

	return on_message_topic(msg)

def callback__currentLoc(data):
	global ws, ws_lock
	d = message_converter.convert_ros_message_to_dictionary(data)
	d['topic'] = '/currentLoc' 
	rospy.loginfo('monitor has observed the following message on topic '+d['topic']+ ":\n" + str(data))
	d['time'] = rospy.get_time()
	ws_lock.acquire()
	while d['time'] in dict_msgs:
		d['time'] += 0.01
	ws.send(json.dumps(d))
	dict_msgs[d['time']] = data
	msg = ws.recv()
	ws_lock.release()

	return on_message_topic(msg)

		
def monitor():
	global pub_error, pub_verdict
	with open(log, 'w') as log_file:
		log_file.write('')

	rospy.init_node('radiation_varanus', anonymous=True)
	pub_error = rospy.Publisher(name = 'radiation_varanus/monitor_error', data_class = MonitorError, latch = True, queue_size = 1000)
	pub_verdict = rospy.Publisher(name = 'radiation_varanus/monitor_verdict', data_class = String, latch = True, queue_size = 1000)
	rospy.Subscriber('/radiation_sensor_plugin/sensor_0', Simulated_Radiation_Msg, callback__radiation_sensor_plugin_sensor_0)
	rospy.Subscriber('/command', Command, callback__command)
	rospy.Subscriber('/inspected', Inspection, callback__inspected)
	rospy.Subscriber('/currentLoc', Int16, callback__currentLoc)
	rospy.loginfo('monitor started and ready')

def on_message_topic(message):
	global error, log, actions
	json_dict = json.loads(message)
	verdict = json_dict['verdict']
	topic = json_dict['topic']
	msg = dict_msgs[json_dict['time']]

	if verdict == 'true' or verdict == 'currently_true' or verdict == 'unknown':
		if verdict == 'true' and not pub_dict:
			rospy.loginfo('The monitor concluded the satisfaction of the property under analysis, and can be safely removed.')
			ws.close()
			exit(0)
		else:
			logging(json_dict)
			rospy.loginfo('The event ' + message + ' is consistent and republished')
			if topic in pub_dict:
				pub_dict[topic].publish(msg)
			del dict_msgs[json_dict['time']]
	else:
		logging(json_dict)
		rospy.loginfo('The event ' + message + ' is inconsistent.')
		publish_error('topic', topic, json_dict)
		if verdict == 'false' and not pub_dict:
			rospy.loginfo('The monitor concluded the violation of the property under analysis, and can be safely removed.')
			ws.close()
			exit(0)
		if actions[topic][0] != 'filter':
			if topic in pub_dict:
				pub_dict[topic].publish(msg)
			del dict_msgs[json_dict['time']]
	publish_verdict(verdict)

def on_message_service_request(message):
	global error, log, actions, ws
	json_dict = json.loads(message)
	verdict = str(json_dict['verdict'])
	service = json_dict['service']
	
	logging(json_dict)
	if verdict == 'true' or verdict == 'currently_true' or verdict == 'unknown':
		rospy.loginfo('The event ' + message + ' is consistent and the service '+ str(service)+' is called.')
		del json_dict['verdict']
		rospy.wait_for_service(service)
		json_dict = call_service(service, srv_type_dict[service], json_dict)
		del json_dict['request']
		msg = get_oracle_verdict(json_dict)
		return on_message_service_response(msg)
	else:
		rospy.loginfo('The request ' + message + ' is inconsistent.')
		publish_error('service', service, json_dict)
		publish_verdict(verdict)
		if actions[service][0] != 'filter':
			if 'verdict' in json_dict: del json_dict['verdict']
			rospy.wait_for_service(service)
			json_dict = call_service(service, srv_type_dict[service], json_dict)
			del json_dict['request']
			msg = get_oracle_verdict(json_dict)
			return on_message_service_response(msg)
		else:
			res.error = True
			dict_msgs[json_dict['time']] = res
			raise Exception('The request violates the monitor specification, so it has been filtered out.')
			return res

def on_message_service_response(message):
	global error, log, actions, ws
	json_dict = json.loads(message)
	verdict = str(json_dict['verdict'])
	service = json_dict['service']

	logging(json_dict)
	if verdict == 'true' or verdict == 'currently_true' or verdict == 'unknown':
		rospy.loginfo('The response ' + message + ' is consistent, the result is returned.')
		return dict_msgs[json_dict['time']]
	else:
		rospy.loginfo('The response ' + message + ' is inconsistent.')
		publish_error('service', service, json_dict)
		publish_verdict(verdict)
		if actions[service][0] != 'filter':
			return dict_msgs[json_dict['time']]
		else:
			res.error = True
			dict_msgs[json_dict['time']] = res
			raise Exception('The response violates the monitor specification, so it has been filtered out.')
			return res


def get_oracle_verdict(json_dict):
	global ws_lock, ws
	ws_lock.acquire() #lock
		
	ws.send(json.dumps(json_dict))
	msg = ws.recv()
		
	ws_lock.release() #unlock
	return msg

def publish_verdict(verdict):
	verdict_msg = String()
	verdict_msg.data = verdict
	pub_verdict.publish(verdict_msg)




def publish_error(topic_or_service, name, json_dict):
	global dict_msgs, error
	error = MonitorError()
	if topic_or_service == 'service':
		error.m_service = name
	else:
		error.m_topic = name
	error.m_time = json_dict['time']
	#error.m_property = json_dict['spec']
	error.m_content = str(dict_msgs[json_dict['time']])
	pub_error.publish(error)
	error=True


def logging(json_dict):
	try:
		with open(log, 'a+') as log_file:
			log_file.write(json.dumps(json_dict) + '\n')
		rospy.loginfo('event logged')
	except Exception as e:
		rospy.loginfo('Exception: '+str(e)+'\nUnable to log the event.')

def main(argv):
	global log, actions, ws
	log = './log_radiation_varanus.txt' 
	actions = {
		'/radiation_sensor_plugin/sensor_0' : ('log', 1), 
		'/command' : ('log', 1), 
		'/inspected' : ('log', 1), 
		'/currentLoc' : ('log', 1)
	}
	websocket.enableTrace(True)
	ws = websocket.WebSocket()
	ws.connect('ws://127.0.0.1:5087')
	rospy.loginfo('Websocket is open')
	monitor()
	rospy.spin()

if __name__ == '__main__':
	main(sys.argv)