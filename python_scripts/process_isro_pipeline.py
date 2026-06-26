import glob
import os
import cdflib
import numpy as np
import pandas as pd


def extract_isro_pipeline_features(data_folder):
    # Find all CDF files in the target directory
    cdf_files = sorted(glob.glob(os.path.join(data_folder, "*.cdf")))

    goes_dfs = []
    wind_dfs = []

    print(f"Found {len(cdf_files)} total CDF files in '{data_folder}'")
    print("-" * 60)

    for file in cdf_files:
        file_name = os.path.basename(file)
        file_name_lower = file_name.lower()
        
        try:
            cdf = cdflib.CDF(file)
            # Gather all variables natively stored within the file structure
            all_vars = cdf.cdf_info().zVariables + cdf.cdf_info().rVariables

            # 1. Robust Time Extraction handling different CDF types
            epoch_var = [v for v in all_vars if "epoch" in v.lower()][0]
            epochs = cdf.varget(epoch_var)
            
            try:
                timestamps = cdflib.epochs.CDFepoch.to_datetime(epochs)
            except Exception:
                timestamps = cdflib.epochs.CDFepoch.unixtime(epochs)
                timestamps = pd.to_datetime(timestamps, unit='s')

            # --- CASE 1: PROCESSING GOES TARGET FILES ---
            if "goes" in file_name_lower:
                print(f" Parsing GOES Target Variables -> {file_name}")

                flux_var_candidates = [v for v in all_vars if "E2" in v and "flux" in v.lower()]
                if not flux_var_candidates:
                    flux_var_candidates = [v for v in all_vars if "flux" in v.lower() and ("elec" in v.lower() or "e" in v.lower())]
                
                if not flux_var_candidates:
                    print(f"⚠️ Could not find explicit E2 flux variable in {file_name}. Skipping.")
                    continue
                    
                flux_var = flux_var_candidates[0]
                flux = cdf.varget(flux_var)

                if len(flux.shape) > 1:
                    flux = flux[:, 0]

                df = pd.DataFrame({"Timestamp": timestamps, "Electron_Flux": flux})
                df.loc[df["Electron_Flux"] < 0, "Electron_Flux"] = np.nan
                goes_dfs.append(df)

            # --- CASE 2: PROCESSING WIND FEATURE FILES ---
            elif "wi_" in file_name_lower or "wind" in file_name_lower:
                file_dict = {"Timestamp": timestamps}

                # Sub-case 2A: Wind Interplanetary Magnetic Field (MFI)
                if "mfi" in file_name_lower or any("mfi" in v.lower() for v in all_vars):
                    print(f" Parsing Wind IMF Features (MFI) -> {file_name}")

                    b_mag_var = [v for v in all_vars if "B_mag" in v or "F1" in v or "f1" in v.lower()][0]
                    file_dict["Total_Magnetic_Field"] = cdf.varget(b_mag_var)

                    vec_var = [v for v in all_vars if "brtn" in v.lower() or "bgse" in v.lower()][0]
                    vectors = cdf.varget(vec_var)
                    file_dict["Bx"] = vectors[:, 0]
                    file_dict["By"] = vectors[:, 1]
                    file_dict["Bz"] = vectors[:, 2]

                # Sub-case 2B: Wind Plasma Parameters (SWE Key Parameters)
                else:
                    print(f" Parsing Wind Solar Wind Features (SWE) -> {file_name}")

                    # Exact string lookups discovered during debug prints
                    speed_var_candidates = [v for v in all_vars if v in ["V_GSE_p", "V_p", "v_p"] or "speed" in v.lower()]
                    dense_var_candidates = [v for v in all_vars if v in ["Np", "N_p", "n_p"] or "density" in v.lower()]
                    
                    if not speed_var_candidates or not dense_var_candidates:
                        print(f"⚠️ Variable mismatch inside SWE file {file_name}. Skipping.")
                        continue

                    speed_var = speed_var_candidates[0]
                    dense_var = dense_var_candidates[0]

                    v_data = cdf.varget(speed_var)
                    if len(v_data.shape) > 1:
                        # Since V_GSE_p contains vector metrics [Vx, Vy, Vz], compute the magnitude (Speed)
                        file_dict["Solar_Wind_Speed"] = np.linalg.norm(v_data, axis=1)
                    else:
                        file_dict["Solar_Wind_Speed"] = v_data

                    file_dict["Proton_Density"] = cdf.varget(dense_var)

                df = pd.DataFrame(file_dict)

                # Clean instrumentation noise boundaries out
                for col in df.columns:
                    if col != "Timestamp":
                        df.loc[df[col] < -1e5, col] = np.nan
                        df.loc[df[col] > 99999, col] = np.nan

                wind_dfs.append(df)

        except Exception as e:
            print(f"❌ Error parsing {file_name}: {e}")

    print("\n" + "=" * 60 + "\nAggregating and Merging Datasets...")

    # Concatenate matrices vertically 
    df_all_goes = pd.concat(goes_dfs, ignore_index=True).sort_values("Timestamp") if goes_dfs else pd.DataFrame()
    df_all_wind = pd.concat(wind_dfs, ignore_index=True).sort_values("Timestamp") if wind_dfs else pd.DataFrame()

    # Outer join merge matching timestamps
    if not df_all_goes.empty and not df_all_wind.empty:
        master_df = pd.merge_ordered(df_all_goes, df_all_wind, on="Timestamp", how="outer").sort_values("Timestamp")
        master_df.dropna(how="all", subset=[c for c in master_df.columns if c != "Timestamp"], inplace=True)
        return master_df
    else:
        print("Pipeline parsing failed: Check that both GOES and WIND files exist in your folder.")
        return pd.DataFrame()


if __name__ == "__main__":
    DATA_DIR = "./ISRO_data"
    df_raw = extract_isro_pipeline_features(DATA_DIR)

    if not df_raw.empty:
        print("Resampling and interpolating timeline to 5-minute bins...")
        df_raw.set_index("Timestamp", inplace=True)
        
        # Build standard 5-minute interval frames and sync variables linearly [cite: 28, 332]
        df_model = df_raw.resample("5min").mean().interpolate(method="linear")
        
        # --- DERIVED FEATURE: SOLAR WIND DYNAMIC PRESSURE ---
        # Formula: P = 1.6726e-6 * Density * (Speed)^2  --> yields pressure in nanoPascals (nPa)
        if "Proton_Density" in df_model.columns and "Solar_Wind_Speed" in df_model.columns:
            print("Calculating derived feature: Solar Wind Dynamic Pressure...")
            df_model["Dynamic_Pressure"] = 1.6726e-6 * df_model["Proton_Density"] * (df_model["Solar_Wind_Speed"] ** 2)
            
        df_model.reset_index(inplace=True)

        # Output generation
        output_name = "clean_model_features.csv"
        df_model.to_csv(output_name, index=False)

        print(f"\n🎉 Success! Clean dataset created: '{output_name}'")
        print(f"Total rows structured for modeling: {len(df_model)}")
        print("\nPreview of final output file columns:")
        print(df_model[["Timestamp", "Electron_Flux", "Solar_Wind_Speed", "Dynamic_Pressure", "Bz"]].dropna().head(5))
