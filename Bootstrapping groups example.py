##################################################################
# Confidence intervals by group
##################################################################

# Import packages
import numpy as np
import pandas as pd
import itertools

# For plotting
import matplotlib.pyplot as plt

# Create dummy data
number_of_eas = 180
number_of_districts = 5
group_columns = ["Sex", "Age group", "Urban/rural"]


dummy_districts = {"District":range(1,number_of_districts+1),
                   "Sex":["M", "F"], 
                   "Age group": range(1,9),
                   "Urban/rural":["Urban", "Rural"]}


keys, values = zip(*dummy_districts.items())
weights = [dict(zip(keys, v)) for v in itertools.product(*values)]
# this gives us our 160 groups
# of which there are 32 in each district

dummy_ea_populations = pd.DataFrame()
dummy_ea_populations["District"] = np.random.randint(1, number_of_districts+1, number_of_eas)
dummy_ea_populations["EA number"] = range(1,number_of_eas+1)

# Join our groups onto our randomly generated EAs
weights_df = pd.DataFrame(weights)
dummy_ea_populations = dummy_ea_populations.merge(weights_df, how="inner", left_on="District",
                                                  right_on="District")

# Add dummy populations using DSE 
dummy_ea_populations["Census Population"] = np.random.randint(100, 2500, len(dummy_ea_populations))
dummy_ea_populations["PES Population"] = round((dummy_ea_populations["Census Population"]*\
                                                (np.random.random(len(dummy_ea_populations))))/50)
 
# we expect a match rate between 90 and 99%
dummy_ea_populations["Matched records"] = dummy_ea_populations["PES Population"] * .93

# this temp column allows for low numbers to sometimes be rounded down
dummy_ea_populations["temp"] = np.random.random(len(dummy_ea_populations))
dummy_ea_populations.loc[dummy_ea_populations["temp"]>0.5, "Matched records"] =\
                                        np.floor(dummy_ea_populations["Matched records"])
dummy_ea_populations["Matched records"] = round(dummy_ea_populations["Matched records"])
dummy_ea_populations = dummy_ea_populations.drop(columns=["temp"])

# calculate the weights
dummy_ea_populations["Weights"] = (dummy_ea_populations["PES Population"]+1)/ \
                                    (dummy_ea_populations["Matched records"]+1)

dummy_ea_populations["Population"] =  round((((dummy_ea_populations["Census Population"] +1)) *\
                                             (dummy_ea_populations["Weights"])) -1)
dummy_ea_populations["Population"] = dummy_ea_populations["Population"].astype(int)

"""
We've created a dummy dataset with the following structure:
    
 District  EA number Sex  Age group Urban/rural  Census Population  \
0         2          1   M          1       Urban               1493   
1         2          1   M          1       Rural                388   
2         2          1   M          2       Urban                102   
3         2          1   M          2       Rural               1617   
4         2          1   M          3       Urban               2461   

   PES Population  Matched records   Weights  Population  
0            27.0             25.0  1.076923      1608  
1             4.0              4.0  1.000000       388  
2             2.0              1.0  1.500000       154  
3            26.0             24.0  1.080000      1746  
4             7.0              7.0  1.000000      2461  
"""



# Bootstrapping variables
number_of_samples = 200
  

def bootstrap_groups(dummy_ea_populations, number_of_samples, group_columns):
    sample_list =[]
    for i in range(number_of_samples):
        # In each district, for each group, sample once for every EA replacing values each time
        sample_populations = dummy_ea_populations.groupby(["District"]+group_columns)\
                                        .sample(frac=1.0, replace=True, random_state=i)
        
        # now to sum across all sampled values for each group in each district
        summed_sample_populations = sample_populations.groupby(["District"]+group_columns)\
                                                                .agg({'Population': 'sum'})\
                                                                .reset_index() 

        # sum over all EAs to create district populations
        summed_sample_districts = summed_sample_populations.groupby(["District"])\
                                                            .agg({"Population":"sum"})\
                                                            .reset_index() 
        
        # sum over all EAs to create national population total
        summed_sample_districts = summed_sample_districts.append({"District":"National", 
                                        "Population":sum(summed_sample_populations["Population"])}, 
                                       ignore_index=True)
        
        # add in category columns
        for col_ in group_columns:
            summed_sample_districts[col_] = "All" 
            
        # sum over all districts by group to create national population
        summed_sample_groups = sample_populations.groupby(group_columns)\
                                .agg({'Population': 'sum'})\
                                .reset_index() 
        summed_sample_groups["District"] = "National"
        
        
        # combine the different results together
        summed_sample_populations = pd.concat([summed_sample_populations, 
                                               summed_sample_districts, 
                                               summed_sample_groups])
        sample_list.append(summed_sample_populations)
    
    # concat each of the samples together and create a list of all the sampled populations 
    # for each group
    final_group_counts = pd.concat(sample_list)
    final_group_counts = final_group_counts.groupby(["District"]+group_columns)["Population"]\
                                                            .apply(lambda x: x.values.tolist())
    final_group_counts = final_group_counts.reset_index()      

    # finally calculate confidence intervals for each group
    final_group_counts["Confidence interval"] = final_group_counts["Population"].apply(lambda x: 
        np.percentile(x, [2.5, 97.5]))

    return final_group_counts

final_group_counts = bootstrap_groups(dummy_ea_populations, number_of_samples, group_columns)



    
    
    