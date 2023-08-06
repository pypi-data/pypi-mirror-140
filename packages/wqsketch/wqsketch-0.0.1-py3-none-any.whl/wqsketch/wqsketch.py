# Main Ideas from: https://blog.acolyer.org/2019/09/06/ddsketch/
# Did not implement the streaming approach 
# Main take-away from ddsketch: ceil(log, base gamma of x) to transform data into bucket

import numpy as np

#Combining with the idea from XGBoost Stat Quest (https://youtu.be/oRrKeUCEbq8?t=439)
#To weight each sample to change the distribution of the quantiles

def create_sketch(data, alpha = 0.01, weight = np.array([None])):

    if weight.any() == None:
        print("Using unity weights")
        weight = np.ones(len(data))
        
    gamma = (1+alpha) / (1-alpha)
    
    #Splitting data into neg, 0 and positive
    idx = np.where(data<0)[0]
    data_negative = data[idx]
    weight_negative = weight[idx]
    #print(weight_negative)
    
    idx = np.where(data==0)[0]
    zero_present = len(idx) > 0
    zero_bucket_weight = np.sum(weight[idx])
    
    idx = np.where(data>0)[0]
    data_positive = data[idx]
    weight_positive = weight[idx]
    
    #Splitting data into neg, 0 and positive
    data_bucket_negative = np.ceil(np.log(-1.0*data_negative) / np.log(gamma))
    buckets_negative = np.unique(data_bucket_negative)
    
    data_bucket_positive = np.ceil(np.log(data_positive) / np.log(gamma))
    buckets_positive = np.unique(data_bucket_positive)
    
    #Putting the weights into the buckets
    negative_bucket_weights=[]
    positive_bucket_weights=[]

    for i in range(len(buckets_negative)):
        negative_bucket_weights.append(np.sum(weight_negative[np.where(data_bucket_negative==buckets_negative[i])]))
    
    for i in range(len(buckets_positive)):
        positive_bucket_weights.append(np.sum(weight_positive[np.where(data_bucket_positive==buckets_positive[i])]))
    
    #Creating buckets matrix
    buckets_negative = np.flip(buckets_negative).reshape(-1,1)
    a=(np.ones(len(buckets_negative))*-1.0).reshape(-1,1)
    buckets_negative = np.hstack((a,buckets_negative))
    
    buckets_positive = buckets_positive.reshape(-1,1)
    a=(np.ones(len(buckets_positive))).reshape(-1,1)
    buckets_positive = np.hstack((a,buckets_positive))
    
    if zero_present:
        buckets_zero = np.array([[0,0]])
    else:
        buckets_zero = np.array([]).reshape(-1,2)
        
    buckets = np.vstack((buckets_negative, buckets_zero, buckets_positive))
    
    #Creating weights vector
    negative_bucket_weights=np.flip(np.array(negative_bucket_weights))
    positive_bucket_weights=np.array(positive_bucket_weights)
    
    if not zero_present:
        zero_bucket_weight=np.array([])
    
    bucket_weights=np.hstack((negative_bucket_weights,zero_bucket_weight,positive_bucket_weights))
    
    #Summing up all the weights
    sum_weights=np.sum(bucket_weights)
    
    return [buckets, bucket_weights, sum_weights, gamma]

#Used ideas from here: https://www.youtube.com/watch?v=vzHuBhyVfOY
#2/(gamma+1) = 1-alpha. This shifts the top of the bucket back to the middle.  

def calculate_quantile(q, sketch):
    
    [buckets, bucket_weights, sum_weights, gamma] = sketch
    assert 0.0 <= q <= 1.0, "q must be between zero and one"
    rank = q * sum_weights
    running_sum = 0
    
    for i in range(len(buckets)):
        
        running_sum += bucket_weights[i]
        
        if running_sum>rank:
            break
    
    return 2 / (gamma + 1) * (gamma**buckets[i,1]) * (buckets[i,0])

def merge_sketch(sketch_list):
    
    num_sketches = len(sketch_list)
    #print(num_sketches)
    
    #unpack the list of sketches into the various lists
    buckets_list=[]
    bucket_weights_list=[]
    sum_weights_list=[]
    gamma_list=[]
    
    for i in range(num_sketches):
        buckets_list.append(sketch_list[i][0])
        bucket_weights_list.append(sketch_list[i][1])
        sum_weights_list.append(sketch_list[i][2])
        gamma_list.append(sketch_list[i][3])
    
    #no method implemented to handle varying gamma these have to be the same across all merged sketches
    #can scale by log(gamma_old) / log(gamma_new) if really want to handle this
    assert all(gamma==gamma_list[0] for gamma in gamma_list), "Inconsistent Gamma Value"
    
    #print("buckets_list")
    #print(buckets_list)
    buckets_all = np.vstack(buckets_list)
    #print("buckets_all")
    #print(buckets_all)
    buckets = np.unique(buckets_all, axis = 0)
    #print("buckets")
    #print(buckets)
    
    #need to reverse the order of the negative bucket numbers
    neg_buckets = buckets[np.where(buckets[:,0] == -1)][:,1]
    neg_buckets = np.flip(neg_buckets)
    
    #print(buckets.shape)
    #print(neg_buckets.shape)
    
    buckets[0:len(neg_buckets),1] = neg_buckets 
    
    bucket_weights = []
    for i in range(len(buckets)):
        
        running_weight = 0
        for j in range(num_sketches):
            
            weight = bucket_weights_list[j][np.where((buckets_list[j]==buckets[i,:]).all(axis=1))]
            #print(weight)
            
            if weight.size > 0:
                running_weight+=weight[0]
                
        bucket_weights.append(running_weight)
    
    bucket_weights = np.array(bucket_weights)
    
    sum_weights = np.sum(np.array(sum_weights_list))
    
    #take the first gamma, we already assert that they are all the same
    gamma = gamma_list[0]
    
    return [buckets, bucket_weights, sum_weights, gamma]