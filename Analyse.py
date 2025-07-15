import sys
import os
import pandas as pd
import subprocess
import shutil
import glob
import time

output_folder = sys.argv[1]
SU2_path = sys.argv[2]
mach_arg = sys.argv[3]
mach_numbers = [float(x) for x in mach_arg.split(",") if x.strip() != '']
list=os.listdir(output_folder)
sample_names = [file for file in list if "sample_" in file]


for index in range(len(sample_names)):
    sample_name = sample_names[index]
    sample_folder = os.path.join(output_folder, sample_name)

    mesh_file_name = f"mesh_{sample_name}.su2"
    mesh_file_path = os.path.join(sample_folder, mesh_file_name)

    for ma in mach_numbers:
        mach_folder_name = f"{sample_name}_at_{ma}_Ma"
        mach_folder = os.path.join(sample_folder, mach_folder_name)
        if not os.path.exists(mach_folder):
            os.makedirs(mach_folder)

        mach_str = f"{ma:.1f}".replace(".", "_")

        cfg_content = f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                                              %
% SU2 configuration file                                                       %
% Case description: Turbulent flow past the ONERA M6 wing                      %
% Author: Thomas D. Economon                                                   %
% Institution: Stanford University                                             %
% Date: 2014.06.14                                                             %
% File Version 5.0.0 "Raven"                                                   %
%                                                                              %

SOLVER= RANS
KIND_TURB_MODEL= SA
MATH_PROBLEM= DIRECT
RESTART_SOL= NO

MACH_NUMBER= {ma}
AOA= 3.06
SIDESLIP_ANGLE= 0.0
INIT_OPTION= REYNOLDS
FREESTREAM_OPTION= TEMPERATURE_FS
FREESTREAM_TEMPERATURE= 288.15
REYNOLDS_NUMBER= 11.72E6
REYNOLDS_LENGTH= 0.64607
FLUID_MODEL= STANDARD_AIR
GAMMA_VALUE= 1.4
GAS_CONSTANT= 287.058
VISCOSITY_MODEL= SUTHERLAND
MU_REF= 1.716E-5
MU_T_REF= 273.15
SUTHERLAND_CONSTANT= 110.4
CONDUCTIVITY_MODEL= CONSTANT_PRANDTL
PRANDTL_LAM= 0.72
PRANDTL_TURB= 0.90
REF_ORIGIN_MOMENT_X = 0.25
REF_ORIGIN_MOMENT_Y = 0.00
REF_ORIGIN_MOMENT_Z = 0.00
REF_LENGTH= 0.64607
REF_AREA= 0
REF_DIMENSIONALIZATION= FREESTREAM_VEL_EQ_ONE
MARKER_HEATFLUX= ( WING, 0.0 )
MARKER_FAR= ( FARFIELD )
MARKER_SYM= ( SYMMETRY )
MARKER_PLOTTING= ( WING )
MARKER_MONITORING= ( WING )
NUM_METHOD_GRAD= GREEN_GAUSS
CFL_NUMBER= 100
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 1.5, 0.5, 10.0, 100000.0 )
RK_ALPHA_COEFF= ( 0.66667, 0.66667, 1.000000 )
ITER= 999999
LINEAR_SOLVER= FGMRES
LINEAR_SOLVER_PREC= ILU
LINEAR_SOLVER_ERROR= 1E-10
LINEAR_SOLVER_ITER= 10
MGLEVEL= 0
MGCYCLE= V_CYCLE
MG_PRE_SMOOTH= ( 1, 1, 1, 1 )
MG_POST_SMOOTH= ( 0, 0, 0, 0 )
MG_CORRECTION_SMOOTH= ( 0, 0, 0, 0 )
MG_DAMP_RESTRICTION= 0.7
MG_DAMP_PROLONGATION= 0.7
CONV_NUM_METHOD_FLOW= JST
JST_SENSOR_COEFF= ( 0.5, 0.02 )
TIME_DISCRE_FLOW= EULER_IMPLICIT
CONV_NUM_METHOD_TURB= SCALAR_UPWIND
MUSCL_TURB= NO
SLOPE_LIMITER_TURB= VENKATAKRISHNAN
TIME_DISCRE_TURB= EULER_IMPLICIT
CONV_FIELD= DRAG
CONV_STARTITER= 10
CONV_CAUCHY_ELEMS= 100
CONV_CAUCHY_EPS= 1E-6

MESH_FILENAME= {mesh_file_name}
MESH_FORMAT= SU2
MESH_OUT_FILENAME= mesh_out.su2
SOLUTION_FILENAME= {sample_name}_solution_flow_{mach_str}.dat
SURFACE_ADJ_FILENAME= {sample_name}_surface_adjoint_{mach_str}.dat
TABULAR_FORMAT= CSV
CONV_FILENAME= {sample_name}_history_{mach_str}Ma
RESTART_FILENAME= restart_flow.dat
RESTART_ADJ_FILENAME= restart_adj.dat
VOLUME_FILENAME= {sample_name}_flow_{mach_str}Ma
VOLUME_ADJ_FILENAME= adjoint
GRAD_OBJFUNC_FILENAME= of_grad.dat
SURFACE_FILENAME= {sample_name}_surface_flow_{mach_str}Ma
OUTPUT_FILES= (RESTART, PARAVIEW, SURFACE_PARAVIEW)
HISTORY_OUTPUT= (ITER, RMS_RES, LIFT, DRAG)
SCREEN_OUTPUT= (INNER_ITER, WALL_TIME, RMS_DENSITY, RMS_NU_TILDE, LIFT, DRAG)
"""

        config_name = f"config_for_{mach_str}Ma.cfg"
        cfg_path = os.path.join(sample_folder, config_name)

        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(cfg_content)

        print(f"[INFO] Running SU2 for {sample_name} at Mach {ma}...")
        subprocess.run([SU2_path, config_name], cwd=sample_folder)
        print(f"[INFO] SU2 run finished for {sample_name} at Mach {ma}.")

        time.sleep(2)

        files_to_move = [
            f"{sample_name}_history_{mach_str}Ma.csv",
            f"{sample_name}_flow_{mach_str}Ma.vtu",
            f"{sample_name}_surface_flow_{mach_str}Ma.vtu",
            f"config_for_{mach_str}Ma.cfg",
            f"{sample_name}_solution_flow_{mach_str}.dat",
            f"{sample_name}_surface_adjoint_{mach_str}.dat"
        ]

        print(f"[DEBUG] Looking for files to move for {sample_name} at Mach {ma}:")
        for filename in files_to_move:
            print(f"  Searching for: {filename}")

        for filename in files_to_move:
            src = os.path.join(sample_folder, filename)
            dst = os.path.join(mach_folder, filename)

            if os.path.exists(src):
                try:
                    shutil.move(src, dst)
                    print(f"[INFO] Moved {filename} to {mach_folder}")
                except Exception as e:
                    print(f"[ERROR] Failed to move {filename}: {e}")
            else:
                print(f"[WARNING] {filename} not found in {sample_folder}")