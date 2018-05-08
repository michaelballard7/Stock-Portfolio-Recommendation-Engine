# IMPORTING IMPORTANT LIBRARIES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
import preprocessing
import os, sys
import csv

path = "data"
directory = os.fsencode(path)
dirs = os.listdir(path)

for file in list(dirs):
    print(file)

### READ TICKR DATA TO MATCH TOP NAMES OF TOP 75 STOCKS
### WITH TICKR NAMES

Tick_cusip=pd.read_csv("cusip_ticker_mapping.csv")

Ticker=list(Tick_cusip['Ticker'])

result=[]

for file in dirs:
    if file.split(".")[0] in Ticker:



# FOR REPRODUCIBILITY
        np.random.seed(7)

        # IMPORTING DATASET
        cur_file="data/"+str(file)
        dataset = pd.read_csv(cur_file, usecols=[1,2,3,4])
        dataset = dataset.reindex(index = dataset.index[::-1])

       # CREATING OWN INDEX FOR FLEXIBILITY
        obs = np.arange(1, len(dataset) + 1, 1)

        # TAKING DIFFERENT INDICATORS FOR PREDICTION
        OHLC_avg = dataset.mean(axis = 1)
        OHLC_avg_orig = dataset.mean(axis = 1)
        HLC_avg = dataset[['High', 'Low', 'Close']].mean(axis = 1)
        close_val = dataset[['Close']]

        # OHLC AVERAGE WORKS BEST IN TERMS OF PREDICTION

        # PLOTTING ALL INDICATORS IN ONE PLOT
        plt.plot(obs, OHLC_avg, 'r', label = 'OHLC avg')
        plt.plot(obs, HLC_avg, 'b', label = 'HLC avg')
        plt.plot(obs, close_val, 'g', label = 'Closing price')
        plt.legend(loc = 'upper right')
        plt.show()

        # PREPARATION OF TIME SERIES DATASE
        OHLC_avg = np.reshape(OHLC_avg.values, (len(OHLC_avg),1)) # 1664
        scaler = MinMaxScaler(feature_range=(0, 1))
        OHLC_avg = scaler.fit_transform(OHLC_avg)

        # TRAIN-TEST SPLIT
        train_OHLC = int(len(OHLC_avg) * 0.75)
        test_OHLC = len(OHLC_avg) - train_OHLC
        train_OHLC, test_OHLC = OHLC_avg[0:train_OHLC,:], OHLC_avg[train_OHLC:len(OHLC_avg),:]

        # TIME-SERIES DATASET (FOR TIME T, VALUES FOR TIME T+1)
        trainX, trainY = preprocessing.new_dataset(train_OHLC, 5)
        testX, testY = preprocessing.new_dataset(test_OHLC, 5)


        # RESHAPING TRAIN AND TEST DATA
        trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
        testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
        step_size = 5

        # LSTM MODEL
        # =============================================================================
        # The input to every LSTM layer must be three-dimensional.
        #
        # The three dimensions of this input are:
        #
        # Samples. One sequence is one sample. A batch is comprised of one or more samples.
        # Time Steps. One time step is one point of observation in the sample.
        # Features. One feature is one observation at a time step.
        # =============================================================================
        model = Sequential()
        model.add(LSTM(32, input_shape=(1, step_size), return_sequences = True))
        model.add(LSTM(16))
        model.add(Dense(1))
        model.add(Activation('linear'))

        # MODEL COMPILING AND TRAINING
        model.compile(loss='mean_squared_error', optimizer='adagrad') # Try SGD, adam, adagrad and compare!!!
        model.fit(trainX, trainY, epochs=50, batch_size=15, verbose=2)

        # PREDICTION
        trainPredict = model.predict(trainX)
        testPredict = model.predict(testX)

        # DE-NORMALIZING FOR PLOTTING

        trainPredict = scaler.inverse_transform(trainPredict)
        trainY = scaler.inverse_transform([trainY])
        testPredict = scaler.inverse_transform(testPredict)
        testY = scaler.inverse_transform([testY])


        # TRAINING RMSE
        trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
        print('Train RMSE: %.2f' % (trainScore))

        # TEST RMSE
        testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
        print('Test RMSE: %.2f' % (testScore))

        # CREATING SIMILAR DATASET TO PLOT TRAINING PREDICTIONS
        trainPredictPlot = np.empty_like(OHLC_avg)
        trainPredictPlot[:, :] = np.nan
        trainPredictPlot[step_size:len(trainPredict)+step_size, :] = trainPredict

        # CREATING SIMILAR DATASSET TO PLOT TEST PREDICTIONS
        testPredictPlot = np.empty_like(OHLC_avg)
        testPredictPlot[:, :] = np.nan
        testPredictPlot[len(trainPredict)+(step_size*2)+1:len(OHLC_avg)-1, :] = testPredict

        # DE-NORMALIZING MAIN DATASET
        OHLC_avg = scaler.inverse_transform(OHLC_avg)

        # PLOT OF MAIN OHLC VALUES, TRAIN PREDICTIONS AND TEST PREDICTIONS
        plt.plot(OHLC_avg, 'g', label = 'original dataset')
        plt.plot(trainPredictPlot, 'r', label = 'training set')
        plt.plot(testPredictPlot, 'b', label = 'predicted stock price/test set')
        plt.legend(loc = 'upper right')
        plt.xlabel('Time in Days')
        plt.ylabel('OHLC Value of Apple Stocks')
        plt.show()

        # PREDICT FUTURE VALUES
        last_val = OHLC_avg[np.array([-1,-2,-3,-4,-5])]
        last_val=scaler.fit_transform(last_val)
        #last_val_scaled = last_val/last_val
        #next_val = model.predict(np.reshape(last_val, (1,1,step_size)))
        #print ("Last Day Value:", np.asscalar(last_val))
        #print ("Next Day Value:", np.asscalar(last_val*next_val))

        pred_vals=[]
        pred_vals1=[]
        pred_vals1.append(file)
        for i in range(0,5):

                    #last_val_scaled = last_val/last_val
                    print(last_val)
                    next_val = model.predict(np.reshape(last_val, (1,1,step_size)))
                    pred_vals.append(next_val)
                    print(next_val)
                    last_val=np.append(last_val,next_val)
                    last_val=np.delete(last_val,0)

                    #next_vals.append(np.asscalar(model.predict(np.reshape(, (1,1,step_size)))))
                    #last_val1.append(next_vals[i-1]*last_val1[i])
        #pred_vals=scaler.inverse_transform(np.array(pred_vals).reshape(1,5))

        ### Scaling Values back using last 5 values as scale standard
        pred_vals=np.array(pred_vals).reshape(1,5)
        last_val_unscaled=np.array(OHLC_avg_orig[np.array([0,1,2,3,4])]).reshape(1,5)


        scaler = MinMaxScaler(feature_range=(0, 1))
        last_val_scaler = scaler.fit_transform(last_val_unscaled)

        pred_vals_rescaled=scaler.inverse_transform(pred_vals)

        a=list(pred_vals_rescaled)[0]
        pred_vals1.append(a)

        result.append(pred_vals1)

res=pd.DataFrame(result)
res.to_csv('results.csv',index=False, header=False)
# =============================================================================
# with open("result.csv", "a") as res:
#     wr = csv.writer(res, dialect='excel')
#     wr.writerow(last_val1)
# =============================================================================

#result
























































































