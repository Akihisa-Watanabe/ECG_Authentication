# ECG_Authentication
We  implemented user authentication using ECG acquired from a heart rate sensor. The authentication pipeline mainly contains four parts: data acquisition, data preprocessing, feature extraction and authentication(classification).
## How to start
First, please prepare the ECG data by referring to the Data Acquisition chapter below. Second, please run the python script `main.py`.

```
$ python3 main.py
```

As a result, the terminal will display the authentication results as shown below.For the meaning of the authentication result, please read the Authentication chapter. In addition, each process of authentication saves the calculation results in its own directory.


<pre>
$ python3 main.py 
template : user1

test user : score
user1 : 98.74 [%]
user0 : 97.57 [%]
user2 : 96.21 [%]
--------------
template : user0

test user : score
user0 : 91.59 [%]
user2 : 90.05 [%]
user1 : 89.24 [%]
--------------
template : user2

test user : score
user2 : 98.41 [%]
user1 : 96.98 [%]
user0 : 96.86 [%]
--------------
</pre>


## Data Acquisition
>Data acquisition module aims to obtain raw biometric signals, either obtained from wearable devices or directly acquired from available public datasets [^1].

To obtain raw ECG signal, we used a [DFRobot's Gravity series of heart rate sensor](https://wiki.dfrobot.com/Heart_Rate_Monitor_Sensor_SKU__SEN0213) and [Arudino Uno](https://www.switch-science.com/catalog/789/). You can get the code [here](https://github.com/Rvoiiima/research-lib/blob/main/serial-to-csv.py) to read serial data and save as csv file with Python. The data and file format should follow the contents of `format.txt`. The directory structure should be as follows.

<pre>
data
    ├── features
    ├── raw
    ├── result
    └── templates
</pre>

## Data Preprocessing
>Data preprocessing module is applied to filter high-frequency noise and segment signals into periodic cycles.The first step in data preprocessing is signal filtering, which filters the high frequency noise caused by unstable measurement circum stances in the signal capturing stage. Then, filtered signals are segmented into cycles with the same time interval.  [^1]

We constructed our preprocessing, segmentation, and validation pipelines around the Python library [neurokit](https://github.com/neuropsychology/NeuroKit). The code for these operations can be found in `signal_process.py`.

## Feature Extraction
>Feature extraction module aims to extract useful features for classification[^1].

We implemented three features 

1. Fiducial Point (QRS waveform)
2. Mel-Frequency Cepstral Coefficients (MFCC)
3. Autocorrelation Coefficients (ACC).

as in reference [^2]. The functions to compute these features are implemented in `signal_process.py`.

## Authentication (Classification)
>Classification module utilizes template matching method, machine learning algorithm, or deep neural network to classify the given biometrics signals and returns the authentication result[^1].

We used the template matching method for the authentication process. The average value of the Fiducial Point feature (QRS waveform) at each time was used as the signal template. The similarity between the signal template and the signal representation was calculated through DTW distance. These authentication processes are implemented in `create_template.py` and `authentication.py`. However, you should be aware of a few things about the `get_dtw` function in `autenticaiton.py`. First, the DTW distance is normalized by the longer of the two signals being compared. Furthermore, the similarity is implemented as follows

![similarity = (1-DTW distance)\times 100 \quad [\%]](https://latex.codecogs.com/gif.latex?similarity&space;=&space;(1-DTW&space;distance)\times&space;100&space;\quad&space;[\%])

When you run `main.py`, you will see the  DTW based similarity sorted in descending order. The top one is the user who has the highest similarity to the template. In the case shown below, all authentication is successful. For example, when user1 is the template, the similarity with the test data of user1 is 98.74%, which is higher than the test data of other users.

<pre>
$ python3 main.py 
template : user1

test user : score
user1 : 98.74 [%]
user0 : 97.57 [%]
user2 : 96.21 [%]
--------------
template : user0

test user : score
user0 : 91.59 [%]
user2 : 90.05 [%]
user1 : 89.24 [%]
--------------
template : user2

test user : score
user2 : 98.41 [%]
user1 : 96.98 [%]
user0 : 96.86 [%]
--------------
</pre>
## Reference
[^1]: [Recent advances in biometrics-based user authentication for wearable devices: A contemporary survey](https://www.sciencedirect.com/science/article/pii/S1051200421001597)

[^2]: [Pulse ID: The Case for Robustness of ECG as a Biometric Identifier](https://ieeexplore.ieee.org/abstract/document/9231814?casa_token=MSFLdT4NURgAAAAA:bXAhP9l8GxK9Pbwpwi7dtX0ok0htsjG5D1w99tS7Fnb4-E4U2_OfEBcEehfkP_LvbJ8VDZG_tQ)
