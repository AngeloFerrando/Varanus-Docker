/radiation_ws# roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch 
	       roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch gui:=false

/radiation_ws# roslaunch monitor run_monitor.launch 

/ROSMonitoring/oracle/Oracle# python3 oracle.py --discrete --property examples.radiation.radiation_orange --port 8080 --online

/mcapl# java -cp ".:lib/3rdparty/*:bin" ail.mas.AIL ./src/examples/gwendolen/compositional/rain/remote_inspection/remote_inspection.ail



docker exec -it $(docker ps -q) bash || docker exec -it $(docker ps -q) sh

