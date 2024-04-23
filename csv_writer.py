import csv
import os

def write_to_csv(data, filename):
    #controllo se il file esiste 
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        fieldnames = ['X', 'Y','Z']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
                writer.writeheader()


        for row in data:
            x=row[0]
            y=row[1]
            z=row[2]
            writer.writerow({'X': x, "Y": y, "Z": z})
