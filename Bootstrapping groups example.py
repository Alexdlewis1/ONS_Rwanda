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

# Add dummy populations 
dummy_ea_populations["Population"] = np.random.randint(100, 250, len(dummy_ea_populations))


"""
We've created a dummy dataset with the following structure:
    
   District  EA number Sex  Age group Urban/rural  Population
0         1          1   M          1       Urban         161
1         1          1   M          1       Rural         222
2         1          1   M          2       Urban         153
3         1          1   M          2       Rural         222
4         1          1   M          3       Urban         200
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
                                                                .agg({'Population': 'sum'})
                                                                
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



    
    
    