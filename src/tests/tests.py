#%%

import numpy as np

A = np.random.random((3, 4)) + np.random.random((3, 4)) * 1j

B = np.random.random((4, 2)) + np.random.random((4, 2)) * 1j

# A.dtype = complex128

C = A @ B

#%%


r = analyse("~/Downloads/model_quant.tflite", full_report=True)

print(r)

#%%


layer_nmacc = [x["extras"]["n_macc"] for x in r["layers"]]
layer_ram = [x["extras"]["rom_output"]["c_size"] for x in r["layers"]]
layer_names = [x["name"] for x in r["layers"]]
# %%

import seaborn as sns
import matplotlib.pyplot as plt

# %%


#%%


plt.figure(figsize=(19, 6))
chart = sns.barplot(x=layer_names, y=layer_nmacc)
chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment="right")
plt.title("MACC per layer")
plt.show()

# %%
