# Simulation-of-CSMA-CA-performance-in-python

This Repository contains code for the project : Simulation of CSMA/CA performance in python.<br>
This is the project done in WIRELESS NETWORKS, 2023 Course. Group Members: Sagar Suman | Arpit Kumar | Puneet<br>

## How to Run -
Step 1: Clone this repo.<br>
Step 2: pip install -r requirements.txt<br>
Step 3: python main.py<br>

## Short Description for Running:
● You can change Variables defined at the begining to change the behaviour of the simulations.<br>
### Some Important Parameters - 
● Turn "CTS_RTS" to True for running CSMA/CA with RTS/CTS, and false to run without RTS/CTS.<br>
● Change "NUMBER_OF_NODES" accordingingly.<br>
● At the end there are three Functions - <br>
  1. Simple_Run() : It will Run the CSMA/CA for chosen parameters.
  2. Analyze_CTS_RTS(): Uncommenting this will plot the Throughput vs Number of Nodes plot.
  3. Analyze_Collisions(): Uncommenting this will plot Collisions vs Number of Nodes plot.



## Little Background about CSMA/CA : 
● For Wireless cases, detection of collision is not possible and thus techniques like CSMA/CD etc. can not be used.<br>
● Reduced Collisions are ensured by using a variety of techniques like IFS, contention window, and RTS/CTS etc.<br>
● Relatively simplistic protocol that require low-cost and low-power solutions<br>
● CSMA/CA is designed to be fair to all devices on the network, regardless of their location or transmission power.

## CSMA/CA Simulation Algorithm used - 
![alt CSMA/CA Simulation ALGO](https://github.com/sagar19197/Simulation-of-CSMA-CA-performance-in-python/blob/master/IMAGES/flow_chart.JPG?raw=true)<br>
At start, attempt no. K=0. For each consecutive attempt of transmission, K increases by 1. CSMA is applied by sensing if the channel is idle in the device’s vicinity. If it is, instead of directly attempting to transmit, we wait for IFS time, even after that if the channel is still idle we wait for amount of time-slots in contention windows (which consists of R slots of fixed time where R is some random number ranging from 0 to 2^K-1). After that, the device sends a ready-to-send signal to the receiver and if the clear-to-send signal is obtained before timeout the channel is reserved and the transmitter device finally waits for some time and sends the data. If the transmitter receives an acknowledgement back from the receiver, then it means data is successfully transmitted. If not, then variable K is increased by 1 (for next attempt). If the no. of attempts exceeds a specified limit, then this process is aborted. If not, then we try to repeat the process again from the start after a certain amount of random backoff time, as shown.<br><br>

## Implementation Details 
The implementation consists of these major steps in Python using SIMPY:<br>
● Defining the network topology: Determining the total no. of nodes, and connections between nodes etc.<br>
● Defining the simulation parameters: Determining duration of simulation, type of traffic etc.<br>
● Implementation of CSMA/CA algorithm (using the discussed flowchart)<br>
● Simulation of network traffic: traffic between nodes in the network is generated<br>
● Collection of results: Collisions etc. are detected using the simulation and performance of the network based on metrics such as throughput, packet loss and delay etc is calculated.<br>
● Analysis of results: Performance of network under different conditions is observed and analyzed<br>


## RESULTS -

### Without RTS/CTS output - 
![alt CSMA/CA Simulation ALGO](https://github.com/sagar19197/Simulation-of-CSMA-CA-performance-in-python/blob/master/IMAGES/without_RTS.JPG?raw=true)<br>
Here, assumptions are that node takes 1 sec to send data to the router. The acknowledgment by Router also reaches nodes in 1 sec. Node waits for another 1 sec in case ACK isn’t received before proceeding to the next phase (i.e. Incrementing attempt no. K by 1 and backoff time stage).<br>
The Output is explained in detail in the report.

### With RTS/CTS output - 
![alt CSMA/CA Simulation ALGO](https://github.com/sagar19197/Simulation-of-CSMA-CA-performance-in-python/blob/master/IMAGES/WITH_RTS.JPG?raw=true)<br>
Simulation Output with RTS/CTS → On Using RTS/CTS mechanism, since the channel gets reserved for use by that particular node which sent the RTS and other nodes stop their transmission. Temporarily, the chances of collisions are Much less likely and channel is more Efficiently used, which can be seen in the output as well.<br>
Detailed-explanation of output is in the report.

### PLOTS Generated - 
#### Throughput vs Number of Nodes
![alt CSMA/CA Simulation ALGO](https://github.com/sagar19197/Simulation-of-CSMA-CA-performance-in-python/blob/master/IMAGES/throoughput.jpeg?raw=true)<br>
● Analysis 1→As no. of nodes increases in the network, throughput (total no. of packets transferred/total time taken) first increases then decreases.<br>
● Analysis 2→In our case, we see that the throughput is high for without RTS/CTS mechanism (than RTS/CTS) because of the additional overhead of wait-time for all the nodes when channel is reserved by RTS/CTS.<br>

#### Number of Collisions vs Number of Node<br>
![alt CSMA/CA Simulation ALGO](https://github.com/sagar19197/Simulation-of-CSMA-CA-performance-in-python/blob/master/IMAGES/colliosn.jpeg?raw=true)<br>
● Analysis 3→ We see that as no. of nodes increases, the no. of collisions in the network also increases due to more communication and more chances of collision<br>
● Analysis 4→ Wee see that the no. of collisions in RTS/CTS case is lesser than no. of collisions in without RTS/CTS case, as RTS/CTS ensures the channel gets reserved and other nodes stop their transmission temporarily in order to reduce the chances of collisions.<br>

### Conclusion
We conclude that CSMA/CA is a powerful, relatively simplistic protocol that ensures collision avoidance in the wireless network. We also saw how RTS/CTS further improves its efficiency at the cost due to transmission of extra frames. Finally, we plotted some graphs and analyzed each of them carefully in order to back the statements above.
