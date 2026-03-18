FROM ros:noetic
ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
   	ros-noetic-desktop-full \
    ros-noetic-jackal-simulator \
    ros-noetic-jackal-desktop \
    ros-noetic-jackal-navigation \
	ros-noetic-rospy-message-converter \
	ros-noetic-navigation \
	ros-noetic-rosbridge-server \
	python2 \
	libpython2.7 \
	python3-rosdep \
    git \
	python3-pip \
	software-properties-common \
	geany \
	gedit

# install ROSMonitoring
RUN pip3 install websocket_client pyyaml
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get install -y python3.8
RUN git clone https://github.com/autonomy-and-verification-uol/ROSMonitoring
RUN pip3 install reelay

# install VARANUS
ADD ./libpng12-0_1.2.54-1ubuntu1.1_amd64.deb ./
RUN git clone --branch buchi --single-branch https://github.com/autonomy-and-verification/varanus.git
RUN pip3 install pyyaml
RUN add-apt-repository -y ppa:linuxuprising/libpng12
RUN sh -c 'echo "deb http://dl.cocotec.io/fdr/debian/ fdr release\n" > /etc/apt/sources.list.d/fdr.list'
RUN apt-get install -y wget gnupg
RUN wget -qO - http://dl.cocotec.io/fdr/linux_deploy.key | apt-key add -
RUN apt-get update
# install libpng12 (from PPA) before fdr; fall back to local deb if needed
RUN apt-get install -y libpng12-0 || apt-get install -y ./libpng12-0_1.2.54-1ubuntu1.1_amd64.deb
RUN apt-get install -y fdr
RUN ldconfig
RUN if [ -f /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 ]; then \
    ln -s /usr/lib/x86_64-linux-gnu/libpython2.7.so.1.0 /usr/lib/x86_64-linux-gnu/libpython2.6.so.1.0; \
    fi
RUN mkdir -p /etc/pki/tls/certs/
RUN cp /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt

RUN apt-get update

# install remote inspection case study
ADD ./radiation_ws/ ./radiation_ws/

# Install MCAPL to run the agent
RUN git clone https://github.com/mcapl/mcapl.git
RUN add-apt-repository ppa:openjdk-r/ppa && apt-get update
RUN apt-get install -y openjdk-17-jdk
ADD ./RosEnv.java /mcapl/src/examples/gwendolen/compositional/rain/remote_inspection/
ADD ./remote_inspection.ail /mcapl/src/examples/gwendolen/compositional/rain/remote_inspection/
ADD ./java_rosbridge_all.jar /mcapl/lib/3rdparty/
WORKDIR /mcapl
RUN find -name "*.java" > sources.txt
RUN javac -cp ".:lib/3rdparty/*" @sources.txt -d bin

# To be removed once all is in the VARANUS repository
WORKDIR /
ADD ./generate_csp.py /

# build custom ROS packages
WORKDIR /radiation_ws
RUN source /opt/ros/noetic/setup.bash && catkin_make

RUN apt-get update
RUN apt install libtinfo5
RUN apt install -y python-yaml

WORKDIR /

# Install SPOT
RUN wget http://www.lrde.epita.fr/dload/spot/spot-2.12.tar.gz
RUN tar -xf spot-2.12.tar.gz 
WORKDIR /spot-2.12
RUN ./configure --prefix ~/.local
RUN make
RUN make install

WORKDIR /

RUN git clone https://github.com/AngeloFerrando/MultiModelPredictiveRuntimeVerification.git

# ADD csp .
ADD rover_model3.csp ./varanus/inspection-rover-test/
ADD rover_defs3.csp ./varanus/inspection-rover-test/
ADD rover_model3.yaml ./varanus/inspection-rover-test/
ADD monitor.py ./varanus/varanus-python/
ADD system_interface.py ./varanus/varanus-python/

# default command
CMD ["bash"]
