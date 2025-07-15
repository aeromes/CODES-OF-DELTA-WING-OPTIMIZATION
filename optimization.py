import sys
import os
import pandas as pd
import random
import numpy as np

output_folder = sys.argv[1]
mach_arg = sys.argv[2]
mach_numbers = [float(x) for x in mach_arg.split(",") if x.strip() != '']
list=os.listdir(output_folder)
sample_names = [file for file in list if "sample_" in file]
coefficients=sys.argv[3]
coefficients_numbers = [float(x) for x in coefficients.split(",") if x.strip() != '']
data=[]

for index in range(len(sample_names)):
    sample_name = sample_names[index]
    current_directory=os.path.join(output_folder, sample_name)
    ratio=[]
    row=[]
    for i in range(len(mach_numbers)):
        ma=mach_numbers[i]
        mach_folder_name = f"{sample_name}_at_{ma}_Ma"
        mach_folder = os.path.join(current_directory, mach_folder_name)
        mach_str = f"{ma:.1f}".replace(".", "_")
        history_name=f"{sample_name}_history_{mach_str}Ma.csv"
        history_path=os.path.join(mach_folder, f"{sample_name}_history_{mach_str}Ma.csv")
        hist=pd.read_csv(history_path)
        hist.columns = hist.columns.str.strip().str.strip('"')
        cl=hist["CL"].iloc[-1]
        cd=hist["CD"].iloc[-1]
        ratio.append(cl/cd)
    total=np.dot(ratio,coefficients_numbers)
    row.append(total)
    data.append(row)

df = pd.DataFrame(data,index=sample_names,columns=["TOTAL RATIO"])
df.to_csv(os.path.join(output_folder,"sample points.csv"), index_label="SAMPLE NAME")
max_value = df["TOTAL RATIO"].max()
max_sample = df["TOTAL RATIO"].idxmax()
print(f"Max Ratio: {max_value}")
print(f"Most optimize Sample: {max_sample}")