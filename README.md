# Federated_Learning_Horizontal
An Implementation of the Federated Averaging Algorithm as described in the Paper - [Communication-Efficient Learning of Deep Networks from Decentralized Data by H. Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson, Blaise Agüera y Arcas](https://arxiv.org/abs/1602.05629) 

![]()

## Description
This repository contains code to implement the Federated Averaging Algorithm as described in in the Paper - Communication-Efficient Learning of Deep Networks from Decentralized Data.
The code consists of:
- <b>FederatedAveraging_Android</b>: An Android Application that 
<br> 1. Uses the TensorFlow for Java API to perform On-Device Training
<br> 2. Sends weights to the Server as well as receives model from the server
- <b>FederatedAveragingServer</b>: A Web Application that:
<br> 1. Receives model weights from various devices
<br> 2. Uses the FederatedAveraging algorithm to aggregate the weights and update the global model.
<br> 3. Push the weights to the client devices
