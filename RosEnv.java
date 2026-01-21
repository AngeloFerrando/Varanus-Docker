package gwendolen.compositional.rain.remote_inspection;

import com.fasterxml.jackson.databind.JsonNode;

import ail.mas.DefaultEnvironment;
import ail.syntax.Action;
import ail.syntax.Literal;
import ail.syntax.NumberTerm;
import ail.syntax.NumberTermImpl;
import ail.syntax.Unifier;
import ail.util.AILexception;
import ros.Publisher;
import ros.RosBridge;
import ros.RosListenDelegate;
import ros.SubscriptionRequestMsg;
import ros.msgs.geometry_msgs.Twist;
import ros.msgs.geometry_msgs.Vector3;
import ros.msgs.move_base_msgs.MoveBaseActionResult;
import ros.msgs.monitor_msgs.MonitorError;
import ros.msgs.remote_inspection_msgs.Inspection;
import ros.msgs.remote_inspection_msgs.Command;
import ros.msgs.remote_inspection_msgs.Radiation;
import ros.msgs.std_msgs.PrimitiveMsg;
import ros.tools.MessageUnpacker;
import ros.tools.PeriodicPublisher;

public class RosEnv extends DefaultEnvironment{
	static final String logname = "gwendolen.ros.turtlebot3.turtlebotworld.RosEnv";
	
	RosBridge bridge = new RosBridge();
	
	int currentLoc = 0;
	boolean goingDoor = false;
	
	float radiation = 0;
	
	public RosEnv() {
		super();
		
		bridge.connect("ws://localhost:9090", true);
		System.out.println("Environment started, connection with ROS established.");
		
		bridge.subscribe(SubscriptionRequestMsg.generate("/move_base/result")
				.setType("move_base_msgs/MoveBaseActionResult"),
//				.setThrottleRate(1)
//				.setQueueLength(1),
			new RosListenDelegate() {
				public void receive(JsonNode data, String stringRep) {
					MessageUnpacker<MoveBaseActionResult> unpacker = new MessageUnpacker<MoveBaseActionResult>(MoveBaseActionResult.class);
					MoveBaseActionResult msg = unpacker.unpackRosMessage(data);
					clearPercepts();
//					System.out.println("Frame id: "+msg.header.frame_id);
//					System.out.println("Stamp sec: "+msg.header.stamp.secs);
//					System.out.println("Seq: "+msg.header.seq);
//					System.out.println("Goal: "+msg.status.goal_id.id);
//					System.out.println("Stamp sec: "+msg.status.goal_id.stamp.secs);
//					System.out.println("Status: "+msg.status.status);
//					System.out.println("Text: "+msg.status.turrext);
//					
//					System.out.println();
					if (goingDoor) {
						currentLoc = 0;
					} else {
						currentLoc++;
					}
					
					update_topics();
					Literal movebase_result = new Literal("movebase_result");
					movebase_result.addTerm(new NumberTermImpl(msg.header.seq));
					movebase_result.addTerm(new NumberTermImpl(msg.status.status));
					addPercept(movebase_result);
				}
			}
	    );
		
		bridge.subscribe(SubscriptionRequestMsg.generate("/radiation_monitor_orange/monitor_error")
				.setType("monitor/MonitorError"),
			new RosListenDelegate() {
				public void receive(JsonNode data, String stringRep) {
					System.out.println("Danger Orange detected by monitor");
					Literal danger = new Literal("danger_orange");
					addPercept(danger);
				}
			}
	    );
		
		
		bridge.subscribe(SubscriptionRequestMsg.generate("/radiation_sensor_plugin/sensor_0")
				.setType("gazebo_radiation_plugins/Simulated_Radiation_Msg"),
//				.setThrottleRate(1)
//				.setQueueLength(1),
			new RosListenDelegate() {
				public void receive(JsonNode data, String stringRep) {
					MessageUnpacker<Radiation> unpacker = new MessageUnpacker<Radiation>(Radiation.class);
					Radiation msg = unpacker.unpackRosMessage(data);
//					clearPercepts();
//					System.out.println("Frame id: "+msg.header.frame_id);
//					System.out.println("Stamp sec: "+msg.header.stamp.secs);
//					System.out.println("Seq: "+msg.header.seq);
//					System.out.println("Goal: "+msg.status.goal_id.id);
//					System.out.println("Stamp sec: "+msg.status.goal_id.stamp.secs);
//					System.out.println("Status: "+msg.status.status);
//					System.out.println("Text: "+msg.status.text);
//					
//					System.out.println("@@@@@@@@@@@@@ Radiation: "+msg.value);
					radiation = msg.value;
//					movebase_result.addTerm(new NumberTermImpl(msg.header.seq));
//					movebase_result.addTerm(new NumberTermImpl(msg.status.status));
				}
			}
	    );
		
	}
	
	/*
	 * (non-Javadoc)
	 * @see ail.mas.DefaultEnvironment#executeAction(java.lang.String, ail.syntax.Action)
	 */
	public Unifier executeAction(String agName, Action act) throws AILexception {
		String actionname = act.getFunctor();
		int nterms = act.getTermsSize();
		if ((actionname.equals("move")) && nterms == 6) {
			NumberTerm lx = (NumberTerm) act.getTerm(0);
			NumberTerm ly = (NumberTerm) act.getTerm(1);
			NumberTerm lz = (NumberTerm) act.getTerm(2);
			NumberTerm ax = (NumberTerm) act.getTerm(3);
			NumberTerm ay = (NumberTerm) act.getTerm(4);
			NumberTerm az = (NumberTerm) act.getTerm(5);
			move(lx.solve(),ly.solve(),lz.solve(),ax.solve(),ay.solve(),az.solve());
		} else if ((actionname.equals("move")) && nterms == 3) {
			NumberTerm lx = (NumberTerm) act.getTerm(0);
			NumberTerm ly = (NumberTerm) act.getTerm(1);
			NumberTerm lz = (NumberTerm) act.getTerm(2);
			move(lx.solve(),ly.solve(),lz.solve());
		} else if (actionname.equals("keep_moving")) {
			NumberTerm period = (NumberTerm) act.getTerm(0);
			NumberTerm lx = (NumberTerm) act.getTerm(1);
			NumberTerm ly = (NumberTerm) act.getTerm(2);
			NumberTerm lz = (NumberTerm) act.getTerm(3);
			NumberTerm ax = (NumberTerm) act.getTerm(4);
			NumberTerm ay = (NumberTerm) act.getTerm(5);
			NumberTerm az = (NumberTerm) act.getTerm(6);
			keep_moving((int) period.solve(),lx.solve(),ly.solve(),lz.solve(),ax.solve(),ay.solve(),az.solve());
		} else if (actionname.equals("stop_moving")) {
			stop_moving();
		} else if (actionname.equals("inspect")) {
		try {
			send_inspect();
			Thread.sleep(3000);
			receive_inspect();
			Literal inspected = new Literal("inspected");
			inspected.addTerm(new NumberTermImpl(currentLoc));
			addPercept(inspected);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		} else if (actionname.equals("update_door")) {
				goingDoor = true;
		} else if (actionname.equals("wait")) {
			NumberTerm period = (NumberTerm) act.getTerm(0);
		try {
			Thread.sleep((int) period.solve());
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
		
		return super.executeAction(agName, act);
	}
	
	public void send_inspect() {
		Publisher fake = new Publisher("command", "gazebo_radiation_plugins/Command", bridge);
		fake.publish(new Command("inspect",currentLoc));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void receive_inspect() {
		// System.out.println("Should print true now.");
		Publisher inspected2 = new Publisher("inspected", "gazebo_radiation_plugins/Inspection", bridge);
		inspected2.publish(new Inspection(currentLoc));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		String status = null;
		System.out.println("Radiation: " + radiation);
		/*if (radiation >= 250 ) {
			status = "red";
			Literal rad = new Literal("danger_red");
			addPercept(rad);
		} else if (radiation >= 120) {
			status = "orange";
			Literal rad = new Literal("danger_orange");
			addPercept(rad);
		} else {
			status = "green";
		}*/

		Publisher radstatus = new Publisher("radiationStatus", "std_msgs/String", bridge);
		radstatus.publish(new PrimitiveMsg<String>(status));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void move(double lx, double ly, double lz, double ax, double ay, double az) {
		Publisher cmd_vel = new Publisher("/cmd_vel", "geometry_msgs/Twist", bridge);
		
		Vector3 linear = new Vector3(lx,ly,lz);
		Vector3 angular = new Vector3(ax,ay,az);
		cmd_vel.publish(new Twist(linear, angular));
	}
	
	public void move(double lx, double ly, double lz) {
		int nextLoc = 0;
		if (!goingDoor) {
			nextLoc = currentLoc + 1;
		}
		Publisher fake = new Publisher("command", "gazebo_radiation_plugins/Command", bridge);
		fake.publish(new Command("move",nextLoc));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		Publisher move_base = new Publisher("/gwendolen_to_move_base", "geometry_msgs/Vector3", bridge);
		move_base.publish(new Vector3(lx,ly,lz));

		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void keep_moving(int period, double lx, double ly, double lz, double ax, double ay, double az) {
		PeriodicPublisher cmd_vel = new PeriodicPublisher("/cmd_vel", "geometry_msgs/Twist", bridge);
		
		Vector3 linear = new Vector3(lx,ly,lz);
		Vector3 angular = new Vector3(ax,ay,az);
		cmd_vel.beginPublishing(new Twist(linear, angular), 2000);
	}

	public void stop_moving() {
		Publisher cmd_vel = new Publisher("/cmd_vel", "geometry_msgs/Twist", bridge);
		
		Vector3 linear = new Vector3(0.0,0.0,0.0);
		Vector3 angular = new Vector3(0.0,0.0,0.0);
		cmd_vel.publish(new Twist(linear, angular));
	}
	
	public void update_topics() {
		Publisher current_loc = new Publisher("currentLoc", "std_msgs/Int16", bridge);
		current_loc.publish(new PrimitiveMsg<Integer>(currentLoc));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		// System.out.println("Should print false now.");
		/*Publisher inspected = new Publisher("inspected", "gazebo_radiation_plugins/Inspection", bridge);
		inspected.publish(new Inspection(currentLoc,"false"));
		
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}*/
	}
	
	@Override
	public boolean done() {
		return false;
	}

}

	
