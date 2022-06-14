# Import packages
import numpy as np
import pandas as pd

# For plotting
import matplotlib.pyplot as plt

# Create dummy data
number_of_eas = 180
number_of_districts = 5
dummy_ea_populations = pd.DataFrame()
dummy_ea_populations["Population"] = np.random.randint(100, 250, number_of_eas)
dummy_ea_populations["District"] = np.random.randint(1, number_of_districts+1, number_of_eas)


# Dummy data distribution
plt.hist(dummy_ea_populations["Population"],bins=30)
plt.title("Dummy EA Populations")
plt.ylabel("Frequency")
plt.xlabel("Population in EAs")
plt.show()



# Sample for each EA
number_of_samples = number_of_eas
number_of_bootstraps = 10000



# Create empty output array
bootstrapped_population = np.empty(number_of_bootstraps, dtype=int)

for i in range(number_of_bootstraps):
    # In each district, sample once for every EA replacing values each time
    sample = dummy_ea_populations.groupby("District")["Population"].sample(frac=1.0, replace=True, random_state=i)
    
    # sum this sample to obtain a total population value
    sample_population = sum(sample)
    bootstrapped_population[i] = sample_population


# Plot the distribution of these samples' total populations
plt.hist(bootstrapped_population,bins=30,density=True)
plt.axvline(x=np.percentile(bootstrapped_population,[2.5]), ymin=0, ymax=1,label='2.5th percentile',c='g')
plt.axvline(x=np.percentile(bootstrapped_population,[97.5]), ymin=0, ymax=1,label='97.5th percentile',c='k')
plt.xlabel("Population Total")
plt.ylabel("PDF")
plt.title("Probability Density Function")
plt.legend()
plt.show()

# Return the confidence intervals
confidence_interval = np.percentile(bootstrapped_population, [2.5, 97.5])
print("2.5 and 97.5% Confidence interval: ", confidence_interval)


