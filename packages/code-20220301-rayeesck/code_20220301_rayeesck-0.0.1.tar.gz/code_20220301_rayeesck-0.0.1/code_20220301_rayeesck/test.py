# from solution import process
from code_20220301_rayeesck import process

if __name__ == "__main__":

    output = process('data.json',output_format = 'csv')

    print(f"No. of Overweight People : {output}")