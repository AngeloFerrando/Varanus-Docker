/radiation_ws# roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch 
	       roslaunch gazebo_radiation_plugins radiation_demonstrator_agent.launch gui:=false

/radiation_ws# 5088!!!roslaunch monitor run_monitor.launch 

/ROSMonitoring/oracle/Oracle# python3 oracle.py --discrete --property examples.radiation.radiation_orange --port 8080 --online

/mcapl# java -cp ".:lib/3rdparty/*:bin" ail.mas.AIL ./src/examples/gwendolen/compositional/rain/remote_inspection/remote_inspection.ail



docker exec -it $(docker ps -q) bash || docker exec -it $(docker ps -q) sh

pkill -9 gzserver && pkill -9 gzclient


python3 monitor.py ../varanus/inspection-rover-test/rover_model3.yaml "F mission_complete"   --online   --varanus-script ../varanus/varanus-python/varanus.py   --varanus-python /usr/bin/python2.7