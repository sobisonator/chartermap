import pandas as pd

sheets_to_read = ["WitnessLookup-PairCombiner",
                  "WitnessLookup-Witnesses",
                  "WitnessLookup-Main",
                  "Diplomas",
                  "Places of issue",
                  "Estates",
                  "Agents"]

master = pd.read_excel("Charter Map master sheet.xlsx",sheets_to_read)

tableau_columns = ["Type of object",
                   "Connection between",
                   "Path",
                   "Object name",
                   "Latitude",
                   "Longitude",
                   "Diploma (filter)",
                   "Full date of issue",
                   "Earliest possible date of issue (filter)",
                   "Latest possible date of issue (filter)",
                   "Authenticity (as in Notion)",
                   "Authenticity (quadripartite simplification) (filter)",
                   "Donor (filter)",
                   "Beneficiary (filter)",
                   "Beneficiary: person or community (filter)",
                   "Beneficiary person: lay or clergy (filter)",
                   "Promulgaiton site (filter)","Estate (filter)",
                   "Distance (m) (filter)","Distance (km) (filter)",
                   "Witness (filter)","Witness's traceability (%) (filter)",
                   "Number of shared witnesses (filter)",
                   "Total no. of witnesss at promulgation site (filter)",
                   "Promulgation site #1 no. of shared witnesses as pct of total witnesses (filter)",
                   "Promulgation site #2 no. of shared witnesses as pct of total witnesses (filter)",
                   #"Is line", # Redundant?
                   "Line label",
                   "Diploma(s)",
                   "Date(s)",
                   "Witnesses",
                   "Promulgation site(s)"]

# Initialise the df for the tableau table, but do not fill it row-by-row
tableau = pd.DataFrame(data = None, index = None, columns = tableau_columns)
# We will prepare rows by adding them into a list of dicts
# with each dict containing the col (key) : value for one row


# Process:

# 1. Iterate through the unique !Null witnesses in WitnessLookup-Main where "Place of issue" != Null
# 2. For each witness, make a list of all places of issue in which it appears
# 3. For each witness, make a list of all charters in which it appears
# 4. For each witness' POI, iterate through all charters in which it appears also in witness scope
# 5. create Line rows for every other place of issue until all in list done
# i.e., once on second, ignore first, etc.
# 5.a. The Line row's content is vaguely:
# POI1,POI2,Lat1,Lon1,Charter




# Let's have some functions to create the different types of rows or row-combinations
def create_tableau_line():
    # Q to self: how to get the index we're at?
    # I think we need to iterate through WitnessLookup-PairCombiner
    tableau_row = {}
    for column in tableau_columns:
        match column:
            case "Type of object":
                tableau_row[column] = "line"
            case "Connection between":
                tableau_row[column] = f"{master["WitnessLookup-PairCombiner"]["Place 1"]} - {master["WitnessLookup-PairCombiner"]["Place 2"]}"
                

print(master)