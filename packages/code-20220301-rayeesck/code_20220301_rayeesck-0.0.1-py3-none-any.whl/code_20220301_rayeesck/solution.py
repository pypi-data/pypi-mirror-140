# import dask
# import numpy as np
import json
import dask.dataframe as dd
import pandas as pd
import os

HEALTH_RISK_DICT = {
    "Underweight" : "Malnutrition risk",
    "Normal weight" : "Low risk",
    "Overweight" : "Enhanced risk",
    "Moderately obese" : "Medium risk",
    "Severely obese" : "High risk",
    "Very severely obese" : "Very high risk"
}

def read_input_file(file_path,n_partitions):
    """ 
    Function to read input file

    Parameters: 
        file_path (string): input file path
        n_partitions (int) : how many partitions to use in dask
        
    Returns: 
        input_data (dataframe) : input dataframe
    """
    ### Read Json file
    # df = dask.delayed(pd.read_json)("data.json")
    df = pd.read_json(file_path)
    input_data = dd.from_pandas(df, npartitions=n_partitions)
    return input_data

def convert_to_numeric(data):
    """ 
    Function to convert object format to numberic

    Parameters: 
        data (dataframe): input dataframe
        
    Returns: 
        data (dataframe): processed dataframe 
    """
    data = dd.to_numeric(data, errors="coerce")#.compute()
    return data

def bmi_category(bmi):
    """ 
    Function to calculate bmi category 

    Parameters: 
        bmi (float): BMI value
        
    Returns: 
        bmi category (string) 
    """
    if bmi <= 18.4 :
        return "Underweight"
    elif bmi >=18.5 and bmi <= 24.9:
        return "Normal weight"
    elif bmi >=25 and bmi <= 29.9:
        return "Overweight"
    elif bmi >=30 and bmi <= 34.9:
        return "Moderately obese"
    elif bmi >= 35 and bmi <= 39.9:
        return "Severely obese"
    elif bmi > 40:
        return "Very severely obese"

def derive_columns(dataframe):
    """ 
    Function add new columns 

    Parameters: 
        dataframe (datafram): input data frame
        
    Returns: 
        dataframe (datafram) : processed dataframe
    """
    dataframe['BMI'] = (dataframe['WeightKg'] / ((dataframe['HeightCm']/100)**2)).round(decimals = 4)
    dataframe['BMI Category'] = dataframe['BMI'].apply(bmi_category, meta=str)#.compute()
    dataframe['Health risk'] = dataframe['BMI Category'].map(HEALTH_RISK_DICT)
    return dataframe

def save_output(data, out_format, input_path):
    """ 
    Function to save output as a file. 

    Parameters: 
        data (dataframe) : output dataframe after processing
        out_format (string) : output file format
        input_path (string) : input file path
    """
    path,file_name = os.path.split(input_path)
    out_file_name = file_name.split(".")[0]
    if out_format == 'csv':
        ## Saving output as csv
        data.compute().to_csv(os.path.join(path,out_file_name+ "_output.csv")) 
    elif out_format == 'json':
        ## Saving output as json
        with open(os.path.join(path,out_file_name+ "_output.json"), 'w') as f:
            json.dump(data.compute().to_dict(orient='records'), f)
    else:
        print("Please choose correct ouput format to store output..!")

def process(json_path, output_format = 'csv'):
    """ 
    Entripoint function. 

    Parameters: 
        json_path (string): input path of json file
        ouput_format (strint) : csv/json, ouput file format
        
    Returns: 
        over_weight_count (integer) : number of overweight people count
    """
    try:
        ## can change based on number of cores
        npartitions = 4
        input_data = read_input_file(json_path,npartitions)
        input_data["HeightCm"] = convert_to_numeric(input_data["HeightCm"])
        input_data["WeightKg"] = convert_to_numeric(input_data["WeightKg"])
        output_data = derive_columns(input_data)
        over_weight_count = (input_data["BMI"] >= 25).sum().compute()
        save_output(output_data,output_format,json_path)
    except Exception as e:
        print(e)
    finally:
        return over_weight_count
    