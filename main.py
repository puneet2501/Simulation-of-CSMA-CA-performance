# WIRELESS NETWORKS, 2023
# MEMBERS - SAGAR SUMAN, ARPIT KUMAR, PUNEET

# CSMA/CA SIMULATIONS - 

import random; 
import numpy as np;
import matplotlib.pyplot as plt
# Importing Simpy
import simpy;


# for total packets 
PACKETS = 0;

# SETUP PARAMETERS USED
RECEIVING_PROCESSING_TIME = 1;
SENDING_NODE_INVOKE_TIME = 0;
SIM_TIME = 20000;


# NUMBER OF NODES IN NETWORK
NUMBER_OF_NODES = 4;


# CSMA/CA PARAMETERS -
# ATTEMPT LIMIT -
ATTEMPT_LIMIT = 10;
# DIFS -
DIFS = 5;
# CONTENTION WIDOW SLOT -
CONTENTION_WINDOW_SLOT = 1;
# SIFS - 
SIFS = 2
# Acknowledgement timers -
ACK_TIMER = 2;
# CARIER SENSING DURATION
CARIER_SENSING_DURATION = 2;


# CTS/RTS MECHANISM TRUE OR FALSE
CTS_RTS = True;

# COVERAGE RANGE - (INCLUDING ITSELF>=1)
COVERAGE_RANGE = 1;
# Coverage Nodes -
COVERAGE_NODES_IDLE = [];
for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
	COVERAGE_NODES_IDLE.append(True); 


Data_senders = 0;

# Variable for ending time -
LAST_TIME = 0;

# VARIABLE FOR COLLISIONS- 
COLLISIONS = 0;
PREVIOUS_COLLISION_TIME = -1;
# RECIEVING NODE -
class RecievingNodes:
	# CONSTRUCTOR
	def __init__(self, env, processing_time):
		self.env = env
		self.processing_time = processing_time
		self.data_senders = 0;
		self.packetType = -1;
		self.request = None;

	# RECIEVE FRAME
	def recieve(self, sending_node):
		global Data_senders, channel, COLLISIONS, PREVIOUS_COLLISION_TIME;
		# TRANSMISSION TIME
		yield self.env.timeout(self.processing_time/2); 
		Data_senders += 1; 
		yield self.env.timeout(self.processing_time/2);
		if( Data_senders > 1):
			print("COLLISION !! GARBAGE DATA RECEIVED AT ROUTER at "+str(self.env.now));
			if (PREVIOUS_COLLISION_TIME != self.env.now):
				COLLISIONS += 1;
				PREVIOUS_COLLISION_TIME = self.env.now;
			yield self.env.timeout(self.processing_time);
		else:
			if self.packetType == 0:
				print("ROUTER RECIEVED RTS FROM Node "+str(sending_node)+" at "+str(self.env.now))
				self.request = channel.request();
				yield self.request
			else:
				print("ROUTER RECIEVED DATA FRAME FROM Node "+str(sending_node)+" at "+str(self.env.now))

		# RECIEVING TIME
		Data_senders -=1;
		yield self.env.timeout(self.processing_time);

	def Release_Request(self):
		global channel
		channel.release(self.request);



# GETTING LOCAL SENSING
def getLocalSensingResult(name):
	global COVERAGE_NODES_IDLE;
	global COVERAGE_RANGE;

	return COVERAGE_NODES_IDLE[(name-1)//COVERAGE_RANGE];

# Setting Local Sesnsing
def setLocalSensingResult(name, value):
	global COVERAGE_NODES_IDLE;
	global COVERAGE_RANGE;

	COVERAGE_NODES_IDLE[(name-1)//COVERAGE_RANGE] = value;



# NODE CLASS -
class NODE:

	def __init__ (self, env):
		self.env = env;
		self.ATTEMPT = 0;
		self.R = 0;


	# Sending Node - 
	def SendingNode(self, env, name, recieving_nodes):
		global PACKETS, DIFS, ATTEMPT, CONTENTION_WINDOW_SLOT, SIFS, LAST_TIME;
		global ACK_TIMER, ATTEMPT_LIMIT, RECEIVING_PROCESSING_TIME, CTS_RTS, channel;


		while self.ATTEMPT < ATTEMPT_LIMIT:
			# CHECKING FOR IDLE
			if CTS_RTS == True:
				request = channel.request();
				yield request;
				channel.release(request);


			while getLocalSensingResult(name) == False:
				yield env.timeout(CARIER_SENSING_DURATION);

			# Waiting for DIFS - 
			if CTS_RTS == True:
				request = channel.request();
				yield request;
				channel.release(request);

			yield env.timeout(random.randint(DIFS, 2*DIFS));

			# Choose Random Number between 0 to 2^Attemp-1
			self.R = random.randint(0, pow(2, self.ATTEMPT));
			# Wait for R slots -
			Contention_Window = self.R*CONTENTION_WINDOW_SLOT;
			# WAITING -
			for slots in range(self.R):
				if CTS_RTS == True:
					request = channel.request();
					yield request;
					channel.release(request);
				# CHECKING FOR IDLE
				while getLocalSensingResult(name) == False:
					yield env.timeout(CARIER_SENSING_DURATION);

				if CTS_RTS == True:
					request = channel.request();
					yield request;
					channel.release(request);
				yield env.timeout(Contention_Window);


			# CHECKING FOR IDLE
			if CTS_RTS == True:
				request = channel.request();
				yield request;
				channel.release(request);
			while getLocalSensingResult(name) == False:
				yield env.timeout(CARIER_SENSING_DURATION);

			# RTS/CTS -
			if CTS_RTS == True:

				# CHECKNG FOR CTS 
				request = channel.request();
				yield request;
				channel.release(request);

				T_rts = float(env.now);
				print(f"RTS SENT BY NODE {name} at {T_rts}");
				recieving_nodes.packetType = 0;
				# Busy
				setLocalSensingResult(name, False);
				yield env.process(recieving_nodes.recieve(name));
				# FREE
				setLocalSensingResult(name, True);

				T_cts = float(env.now);

				if T_cts - T_rts > SIFS:
					# COLLISION
					self.ATTEMPT += 1;
					# BACKOFF COUNTER -
					Tb = self.R * RECEIVING_PROCESSING_TIME;
					print(f"NODE {name} AT ATTEMPT OF  k = {self.ATTEMPT}, BACKOFF TIME = {Tb} at {env.now}");
					# WAITING-
					yield env.timeout(Tb);
				else: 
					# CTS RECIEVED ON TIME - 
					print(f"CTS RECEIVED BY NODE {name} at {T_cts}");
					
					# WAIT AGAIN - 
					yield env.timeout(SIFS);

					# SENDING FRAME 

					T_send_frame = float(env.now);
					recieving_nodes.packetType = 1;
					print(f"FRAME SENT BY NODE {name} at {T_send_frame}");

					# Busy
					setLocalSensingResult(name, False);
					yield env.process(recieving_nodes.recieve(name));
					# FREE
					setLocalSensingResult(name, True);


					T_recieve_frame = float(env.now);
					# ACK recieved with ACK_TIMER condition
					if T_recieve_frame - T_send_frame <= ACK_TIMER :
						print(f"ACK RECEIVED BY NODE {name} at {T_recieve_frame}");
						LAST_TIME = T_recieve_frame;
						PACKETS +=1;
						recieving_nodes.Release_Request();
						break;
					else:
						# COLLISION
						self.ATTEMPT += 1;
						# BACKOFF COUNTER -
						Tb = self.R * RECEIVING_PROCESSING_TIME;
						print(f"NODE {name} AT ATTEMPT OF  k = {self.ATTEMPT}, BACKOFF TIME = {Tb} at {env.now}");
						# WAITING-
						yield env.timeout(Tb);


			else:
			# without CTS/RTS
				# SENDING FRAME 

				T_send_frame = float(env.now);
				print(f"FRAME SENT BY NODE {name} at {T_send_frame}");
				recieving_nodes.packetType = 1;
				# Busy
				setLocalSensingResult(name, False);
				yield env.process(recieving_nodes.recieve(name));
				# FREE
				setLocalSensingResult(name, True);

				T_recieve_frame = float(env.now);
				# ACK recieved with ACK_TIMER condition
				if T_recieve_frame - T_send_frame <= ACK_TIMER :
					print(f"ACK RECEIVED BY NODE {name} at {T_recieve_frame}");
					LAST_TIME = T_recieve_frame;
					PACKETS +=1;
					break;
				else:
					# COLLISION
					self.ATTEMPT += 1;
					# BACKOFF COUNTER -
					Tb = self.R * RECEIVING_PROCESSING_TIME;
					print(f"NODE {name} AT ATTEMPT OF  k = {self.ATTEMPT}, BACKOFF TIME = {Tb} at {env.now}");
					# WAITING-
					yield env.timeout(Tb);








# FUNCTION FOR SETTING UP SENDING NODES -
def setup(env, processing_time, sending_node_interval):
	global NUMBER_OF_NODES;

	recieving_nodes = RecievingNodes(env, processing_time);
	SENDING_NODE_NAME = 0;
	
	while SENDING_NODE_NAME < NUMBER_OF_NODES:
		# INVOKING SENDING NODES AFTER CERTAIN PERIOD OF TIME
		yield env.timeout(sending_node_interval)
		SENDING_NODE_NAME+=1;
		print(f"NODE {SENDING_NODE_NAME} COMES AT {env.now:.2f}: WAITING FOR IDLE")
		node = NODE(env);
		env.process(node.SendingNode(env, SENDING_NODE_NAME, recieving_nodes));


channel = None;
# Function for simply running 
def Simple_RUN():
	env = simpy.Environment();
	# VARIABALE FOR RESOURCE -
	global channel;
	channel = simpy.Resource(env, 1); 

	env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
	env.run(until = SIM_TIME);

	print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));




# Function for RTS/CTS vs No RTS/CTS - time
def Analyze_CTS_RTS():
	global PACKETS, NUMBER_OF_NODES, CTS_RTS, COVERAGE_NODES_IDLE, COVERAGE_RANGE, LAST_TIME;
	# WITHOUT CTS/RTS
	# FOR 100 Nodes one by one
	print("WITHOUT CTS/RTS SIMULATION")
	without_cts_rts = [];
	for nodes in range(1, 31):
		print("\n FOR NUMBER OF NODES = ", nodes);
		CTS_RTS = False;
		NUMBER_OF_NODES = nodes;
		sum_of_time =  [];
		# FOR 100 ITERATIONS
		for i in range(30):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			global channel;
			channel = simpy.Resource(env, 1); 
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));

			sum_of_time.append(PACKETS/LAST_TIME);
		# Taking average and appending
		without_cts_rts.append(sum(sum_of_time)/100);

	
	# WITH CTS/RTS
	# FOR 100 Nodes one by one
	print("WITHS CTS/RTS SIMULATION")
	with_cts_rts = [];
	for nodes in range(1, 31):
		print("\n FOR NUMBER OF NODES = ", nodes);
		CTS_RTS = True;
		NUMBER_OF_NODES = nodes;
		sum_of_time = [];
		# FOR 100 ITERATIONS
		for i in range(30):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			channel = simpy.Resource(env, 1);
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));
			sum_of_time.append(PACKETS/LAST_TIME);
		# Taking average and appending
		with_cts_rts.append(sum(sum_of_time)/100);

	# PLOTTING - 
	plt.figure(figsize = (10, 5))
	Node_list = np.asarray(range(1,31));
	plt.bar(Node_list-0.2, without_cts_rts,0.4, color ='maroon', label = 'Without RTS/CTS');
	plt.bar(Node_list+0.2, with_cts_rts,0.4, color = 'blue', label = 'With RTS/CTS');

	print("WITHOUT CTS/RTS:",without_cts_rts);
	print("WITHS CTS/RTS:",with_cts_rts)

	plt.xlabel("Number of Nodes")
	plt.ylabel("Throughput")
	plt.title("ThroughPut");
	plt.legend();
	plt.show()




# FUNCTION for COLLISONS - 
def Analyze_Collisions():
	global PACKETS, NUMBER_OF_NODES, CTS_RTS, COVERAGE_NODES_IDLE, COVERAGE_RANGE, LAST_TIME, COLLISIONS, PREVIOUS_COLLISION_TIME;
	# WITHOUT CTS/RTS
	# FOR 100 Nodes one by one
	print("WITHOUT CTS/RTS SIMULATION")
	without_cts_rts = [];
	for nodes in range(1, 31):
		print("\n FOR NUMBER OF NODES = ", nodes);
		CTS_RTS = False;
		NUMBER_OF_NODES = nodes;
		sum_of_time =  [];
		# FOR 100 ITERATIONS
		for i in range(30):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			global channel;
			channel = simpy.Resource(env, 1); 
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));

			sum_of_time.append(COLLISIONS);
		# Taking average and appending
		without_cts_rts.append(sum(sum_of_time)/100);

	
	# WITH CTS/RTS
	# FOR 100 Nodes one by one
	print("WITHS CTS/RTS SIMULATION")
	with_cts_rts = [];
	for nodes in range(1, 31):
		print("\n FOR NUMBER OF NODES = ", nodes);
		CTS_RTS = True;
		NUMBER_OF_NODES = nodes;
		sum_of_time = [];
		# FOR 100 ITERATIONS
		for i in range(30):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			channel = simpy.Resource(env, 1);
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));
			sum_of_time.append(COLLISIONS);
		# Taking average and appending
		with_cts_rts.append(sum(sum_of_time)/100);

	# PLOTTING - 
	plt.figure(figsize = (10, 5))
	Node_list = np.asarray(range(1,31));
	plt.bar(Node_list-0.2, without_cts_rts,0.4, color ='maroon', label = 'With RTS/CTS');
	plt.bar(Node_list+0.2, with_cts_rts,0.4, color = 'blue', label = 'Without RTS/CTS');

	print("WITHOUT CTS/RTS:",without_cts_rts);
	print("WITHS CTS/RTS:",with_cts_rts)

	plt.xlabel("Number of Nodes")
	plt.ylabel("Number of Collisions")
	plt.title("Collisions vs Number of Nodes");
	plt.legend();
	plt.show()





# FUNCTION for COVERAGE AREA-
def Analyze_Coverage_Area():
	# INCOMPLTETE METHOD
	global PACKETS, NUMBER_OF_NODES, CTS_RTS, COVERAGE_NODES_IDLE, COVERAGE_RANGE, LAST_TIME;

	# WITHOUT RTS/CTS
	CTS_RTS = False;
	NUMBER_OF_NODES = 10;
	print("WITHOUT CTS/RTS SIMULATION")
	without_cts_rts = [];
	for coverage_area in range(1, 31):
		print("COVERAGE AREA ",coverage_area);
		COVERAGE_RANGE = coverage_area;
		sum_of_time = [];
		# FOR 100 ITERATIONS
		for i in range(1,31):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			global channel;
			channel = simpy.Resource(env, 1);
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));
			sum_of_time.append(PACKETS/LAST_TIME);
		# Taking average and appending
		without_cts_rts.append(sum(sum_of_time)/30);


	# WITH RTS/CTS
	CTS_RTS = True;
	NUMBER_OF_NODES = 10;
	print("WITHs CTS/RTS SIMULATION")
	with_cts_rts = [];
	for coverage_area in range(1, 31):
		print("COVERAGE AREA ",coverage_area);
		COVERAGE_RANGE = coverage_area;
		sum_of_time = [];
		# FOR 100 ITERATIONS
		for i in range(1,31):
			PACKETS = 0;
			COLLISIONS = 0;
			PREVIOUS_COLLISION_TIME = -1;
			print(" FOR Iteration = ", i);
			# Coverage Nodes -
			COVERAGE_NODES_IDLE = [];
			for i in range((NUMBER_OF_NODES//COVERAGE_RANGE) + 1):
				COVERAGE_NODES_IDLE.append(True); 
			env = simpy.Environment();
			channel = simpy.Resource(env, 1);
			env.process(setup(env, RECEIVING_PROCESSING_TIME, SENDING_NODE_INVOKE_TIME));
			env.run(until = SIM_TIME);

			print("TOTAL PACKETS TRANSFERED= "+str(PACKETS));
			sum_of_time.append(PACKETS/LAST_TIME);
		# Taking average and appending
		with_cts_rts.append(sum(sum_of_time)/30);

	print("WITHOUT CTS/RTS:",without_cts_rts);
	print("WITHS CTS/RTS:",with_cts_rts)

	# PLOTTING - 
	plt.figure(figsize = (10, 5))
	Node_list = np.asarray(range(1,31));

	plt.bar(Node_list-0.2, without_cts_rts,0.4, color ='maroon', label = 'Without RTS/CTS');
	plt.bar(Node_list+0.2, with_cts_rts,0.4, color = 'blue', label = 'With RTS/CTS');

	plt.xlabel("Coverage Area")
	plt.ylabel("ThroughPut")
	plt.title("Variation of ThroughPu for 30 packets with and without RTS/CTS for 10 node Network by varying coverage area. [Each Node is sending one packet]");
	plt.legend();
	plt.show()

	



# RUNNING-
print("Starting Simulation of CSMA/CA");
Simple_RUN();
#Analyze_CTS_RTS();
#Analyze_Collisions();
