import os
import csv
### updated 12/03/2024
### added print for parts w/o tools 


def cnc_partlist(job_code,partlist_file):
   
  
    cnc_path = os.path.dirname(partlist_file)  # Use the directory of partlist_file
    # Remove all files except for partlist_file
    #for filename in os.listdir(cnc_path):
        # Full path of the file
        #file_path = os.path.join(cnc_path, filename)
        # Normalize paths for comparison
        #if os.path.abspath(file_path) != os.path.abspath(partlist_file) and os.path.isfile(file_path):
            #os.remove(file_path)  # Delete the file
    
    
    eletypes = 0
    cnc_parts = []
    cnc_headers = []
    
    etypepack = []
    skipped_parts = []
    
    # Read the CNC partlist file
    with open(partlist_file, 'r') as file:
        reader = csv.reader(file)
        lines = [line for line in reader if line and not any('#' in item for item in line[0][:5])]
    
    # Extract headers and exclude from cnc_parts
    I_headers = [item.strip() for item in lines[0]]
    #print(headers)
    raw_cnc_parts = [[item.strip() for item in line] for line in lines[1:]]
    
    # Process each part
    for part in raw_cnc_parts:
        # Exclude parts with less than 5 columns
        if len(part) < 5:
            skipped_parts.append(part)
            continue
        
        try:
            # Create new lists to store expanded parts and headers
            expanded_part = part[:3]  # Preserve the first three columns as-is
            expanded_headers = I_headers[:3]  # Preserve the first three headers as-is
            for i in range(3, len(part)):
                value = part[i].strip() if isinstance(part[i], str) else part[i]
                header = I_headers[i]
                if value:  # Check if the value is not empty or None
                    if isinstance(value, str) and "+" in value and "*" in value:
                        try:
                            # Parse the X+n*D format
                            base, multiplier = value.split("+")
                            X = float(base.strip())
                            n, D = map(float, multiplier.split("*"))
                            n = int(n)  # Ensure n is an integer
                            
                            # Generate the expanded sequence
                            expanded_values = [X + j * D for j in range(n + 1)]
                            
                            # Add the expanded values and duplicate headers
                            expanded_part.extend(expanded_values)
                            expanded_headers.extend([header] * len(expanded_values))
                        except ValueError:
                            # If parsing fails, append the original value and header
                            expanded_part.append(value)
                            expanded_headers.append(header)
                    else:
                        # Try converting the value to a float
                        expanded_part.append(float(value))
                        expanded_headers.append(header)
                else:
                    # Append None for empty or invalid values and preserve the header
                    expanded_part.append(None)
                    expanded_headers.append(header)
        
            # Replace the original part and headers with the expanded versions
            part = expanded_part
            headers = expanded_headers
    
            
        except ValueError:
            # If any conversion fails, store the part in skipped_parts
            skipped_parts.append(part)
            continue
            
        # If successfully processed, add to cnc_parts
        cnc_parts.append(part)
        cnc_headers.append(headers)
    
    # Write the skipped parts to skippedparts.csv for inspection
    if skipped_parts:
        with open(os.path.join(cnc_path, "skippedparts.csv"), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(I_headers)  # Write headers
            writer.writerows(skipped_parts)  # Write skipped lines
    
    # Determine types
    for part in cnc_parts:
        elepack = part[0]
        eletype = part[2]
        if [elepack, eletype] not in etypepack:
            etypepack.append([elepack, eletype])
            eletypes += 1
    
    
    
    # Reorder columns for each part
    def reorder_columns(part):
        # Extract numeric values from part starting at column 5
        reorder_start_idx = 5
        paired_data = list(zip(headers[reorder_start_idx:], part[reorder_start_idx:]))
        filtered_data = [
        (header, value) for header, value in paired_data
        if value not in (None, 0, "0", "0.0")]
        # Sort based on part values (column values)
        paired_data_sorted = sorted(filtered_data, key=lambda x: x[1])
        # Separate reordered headers and values
        headers_reordered = headers[:reorder_start_idx] + [item[0] for item in paired_data_sorted]
        values_reordered = part[:reorder_start_idx] + [item[1] for item in paired_data_sorted]
        return [headers_reordered, values_reordered]
    
    
    
    # Write CNC files
    for pack, profile in etypepack:
        cnc_filename = os.path.join(cnc_path, f"{job_code}_{pack}_{profile}.Parts List")
        thickness = profile.split("-")[1][:2]
        
        with open(cnc_filename, 'w', newline="\r\n", encoding="utf-8") as file:
            file.write("1\n")
            file.write(f"N/{profile}/{thickness}\n")
            
            for nn in range(len(cnc_parts)):
            
                part=cnc_parts[nn]
                headers=cnc_headers[nn]
            
                
                if (part[2] == profile and part[0] == pack and 
                    part[4] > 0 and part[3] > 50):  # qty > 0 and length > 50 mm
                
                    x1, z1, x2, z2 = 0, 0, round(part[3], 0), 0
                    lmm = round(float(part[3]), 1)
                    file.write(f"IN={job_code} CU=SCUSA_50KSI_G90 GA={thickness} PR={profile} PA={pack} QT={part[4]} MM={lmm} DE={part[1]} X1={x1} Y1={z1} X2={x2} Y2={z2} HI=-41\n")
                    
                    prt = 0
                    # print(headers)
                    # print(part)
                    part_matrix = reorder_columns(part)
                    #print (part_matrix)
                    
                    
                   
                    if  len(part_matrix[1])== 5:
                          file.write(f" -1,100.0,{part[1]}\n")
                          prt = 1
                            
                    for i in range(5, len(part_matrix[1])):
                        pos=part_matrix[1][i]
                        tool=part_matrix[0][i]
                        
                        if prt == 0 and pos > 100:
                            file.write(f" -1,100.0,{part[1]}\n")
                            prt = 1
                        if tool == "Index_n":
                            file.write(f" Index,{round(pos, 1)}\n")
                            
                        elif tool == "Swage+Dimple_n":
                            file.write(f" Swage,{round(pos, 1)}\n")
                            file.write(f" Dimple,{round(pos, 1)}\n")
                            
                        elif tool== "Notch+Lip+Dimple_n":
                            file.write(f" Notch,{round(pos, 1)}\n")
                            file.write(f" Lip,{round(pos, 1)}\n")
                            file.write(f" Dimple,{round(pos, 1)}\n")
                            
                        elif tool== "Big Hole_n":
                            file.write(f" Big Hole,{round(pos, 1)}\n")
                        elif tool== "Notch_n":
                            file.write(f" Notch,{round(pos, 1)}\n")
                            
                        elif tool== "Service_n":
                            file.write(f" Service,{round(pos, 1)}\n")
                            
                        elif tool== "Lip_n":
                            file.write(f" Lip,{round(pos, 1)}\n")
                            
                        elif tool== "Dimple_n":
                            file.write(f" Dimple,{round(pos, 1)}\n")
                            
                        elif tool== "Lip+Dimple_n":
                            file.write(f" Lip,{round(pos, 1)}\n")
                            file.write(f" Dimple,{round(pos, 1)}\n")                          


 
# job_code = "SC321"
# partlist_file ='I:/Shared drives/STALO ENGINEERING/STEELCORP SC321 - MODULAR DESIGN/06 STALO TRUSS/04 CNC/G3/PARTLIST FLOOR SC321 - @16.csv'
# cnc_partlist(job_code, partlist_file)

    
