#### WHAT THIS SCRIPT DOES ####
###1.   Attribute and Tag finder for all the collections
###2.   Gets the xml paths of all xmls
###3. write the xml paths, errors in xml paths according to the write tag and attribute

############################################ Imports ############################################
import xml.etree.ElementTree as ET
import csv
from lxml import etree
from os import listdir, sep, path
import re
import ntpath
import pandas as pd
from datetime import datetime
import argparse


####################################### Global Variables #######################################
paths = [] #paths that will be written
errors = [] #Attribute and Tag Errors
Tag_errors = [] #We can have 2 columns for errors
Attrib_errors = [] #We can have 2 columns for errors





# create the parser, add an argument for the input directory, parse the command line arguments
def process_command_line_arguments():
    parser = argparse.ArgumentParser(description='Attribute and Tag finder for all the collections')
    parser.add_argument('-i', '--input_directory', type=str, help='Path to the input directory', required=False)
    parser.add_argument('-oat', '--output_attribsTags', type=str, help='Path to the output attribute and tag list text file', required=False)
    parser.add_argument('-c', '--input_csv', type=str, help='Path to the input directory', required=False)
    parser.add_argument('-o', '--output_directory', type=str, help='Path to the output csv containing paths, frequency and error reports', required=False)

    args = parser.parse_args()

    return args

#<<<<<<<<<<<<<<<<< PART I: Parse xmls and get attribute and tags and write to text file >>>>>>>>>>>>>>>>>>>>>#
#****************** OPTION 1 | Parse xmls and get all the tags and attributes ******************#

#2. Triger the function to get and Write the unique tags and attributes to csv
def MODs(arg):
    modsPaths = []
    files = listdir(arg.input_directory)
    files.sort()
    for file in files:
        if file.endswith(".xml"):
            modsPaths.append("{directory}/{file_name}".format(directory = arg.input_directory, file_name= file))

    return modsPaths


# 1. Parse each XML 
allTags = [] #NEW (All Tags)
allAtrrib = [] #NEW (All Attributes)
uniqueTag_Dict = {} #NEW (Unique TagNames with the number of repitation in a dictionary)
uniqueAttrib_Dict = {} #NEW (Unique Attribute with the number of repitation in a dictionary)
uniqueTag = [] #NEW (Name of the unique attributes)
uniqueAttrib = [] #NEW (Name of the unique Unique Tags)

def MOD_Parse(mods):
    for mod in mods:
        print("Parsing the source MODs for tags/Attributes---------------------------------------- {}".format(mod.split('/')[-1]))
        root = ET.iterparse(mod, events=('start', 'end'))
        #Get all the attribute and tags
        for a,b in root:
            if a == 'start':
                allTags.append(b.tag.split("}")[1])
                if len(b.attrib) > 0:
                    attrib_list = b.attrib
                    for k,v in attrib_list.items():
                        allAtrrib.append(k)

def unique_tag_attrib():
    ##uniqueTag_Dict = {Attribute_Name : Number of repitation}
    tagCheck = []
    for TGs in allTags:
        key = TGs
        if TGs not in tagCheck:
            tagCheck.append(TGs)
            uniqueTag_Dict[key] = 0
        else:
            uniqueTag_Dict[key] += 1

    ##uniqueAttrib_Dict = {Attribute_Name : Number of repitation}
    attribCheck = []
    for att in allAtrrib:
        keys = att
        if att not in attribCheck:
            attribCheck.append(att)
            uniqueAttrib_Dict[keys] = 0
        else:
            uniqueAttrib_Dict[keys] += 1


def dataToCsv(arg):
    data = {
        'atributes': [],
        'atributes frequency' : [],
        'tags': [],
        'tags frequency': []
    }
    
    for att,tg in uniqueAttrib_Dict.items():
        data['atributes'].append(att)
        data['atributes frequency'].append(tg)
    
    for atts,tgs in uniqueTag_Dict.items():
        data['tags'].append(atts)
        data['tags frequency'].append(tgs)

    #fill the columns with less number of rows with empty string
    if len(data['atributes']) != len(data['tags']):
        differnce = len(data['tags']) - len(data['atributes'])
        for insert in range(differnce):
            data['atributes'].append("NONE")
            data['atributes frequency'].append(" ")

    #to write attribute and tags to csv
    df_attTG = pd.DataFrame(data)
    df_attTG.to_csv("{}.csv".format(arg.output_attribsTags), index=0)
    print("An attribute/Tag csv file saved in this directory: {directory}.csv".format(directory = arg))

#<<<<<<<<<<<<<<<<<  Part II: Get the XML Path , check for spelling and errors in each xml path according to Part1 >>>>>>>>>>>>>>>>>>>>>#
def inpute_attribs_tags(arg):
    print("Reading the input csv, containing Attributes and Tags in LDL collections------------------")
    df_attribTags = pd.read_csv(arg.input_csv)
    columnNames = df_attribTags.columns.tolist()
    data_dict =  {}
    for columns in columnNames:
        data_dict[columns] = list(df_attribTags[columns])
    return data_dict

######## Parse and get all the paths and errors ########
def parseAll(mods,csv_input):
    print(csv_input)
    for mod in mods:
        pathName = []
        print("Parsing Target Mods to get xml paths, and error check ---------------------------------------- {}".format(mod.split('/')[-1])) ## IF FOLDER WITHIN FOLDER => CHANGE THE INDEX NUMBER
        root = ET.iterparse(mod, events=('start', 'end'))
        for a,b in root:
            if a == 'start':
                attribs = [] 
                atribValues = []
                WriteAttributes  = []
                attributes = b.attrib
                if len(attributes) > 0:
                    for i,j in attributes.items():
                        attribs.append(i)     #Fixing not printing all the attributes
                        atribValues.append(j)    #Fixing not printing all the attributes Values
                        WriteAttributes.append([i,j]) #write as a list as we go into each attribute

                ### A1) check for any miss-speling in tags and attributes
                        if i not in csv_input["atributes"]:
                            # errors.append(', '.join("{}".format(a[0]) for a in WriteAttributes)) #USED JOIN INSTEAD OF FORMAT
                            errors.append(i) #If we want to have 2 columns for errors for TAGS AND ATTRIBUTES, We can APPEND TO Attrib_errors
                        if b.tag.split("}")[1] not in csv_input["tags"]:
                            errors.append(b.tag.split("}")[1]) #If we want to have 2 columns for errors for TAGS AND ATTRIBUTES, We can APPEND TO Tag_errors
                        else:
                            continue
                ### A2) Print the xmlPath                
                    pathName.append("{} [{}]".format(b.tag.split("}")[1], ", ".join("@{} = '{}'".format(a[0], a[1]) for a in WriteAttributes))) #USED JOIN INSTEAD OF FORMAT
                    yield '/'.join(pathName)

                if len(b.attrib) == 0:
                ### B1) Print the xmlPath                
                    pathName.append("{}".format(b.tag.split("}")[1], b.attrib))
                    yield '/'.join(pathName)

                ### B2) check for any miss-speling in tags(No attributes as these are tags with no attrib)               
                    if b.tag.split("}")[1] not in csv_input["tags"]:
                        errors.append(b.tag.split("}")[1]) #If we want to have 2 columns for errors for TAGS AND ATTRIBUTES, We can APPEND TO Tag_errors
                    else:
                        continue
            else:
                pathName.pop()

        allPaths = []
        for Xpaths in pathName:
            allPaths.append(Xpaths)
    return(allPaths)

######## unique Paths ########
def PathRepeatCheck(ntpath):
    pathsAndCounts= {}
    check = set()
    for p in ntpath:
        if p not in check:
            check.add(p)
            pathsAndCounts[p] = 1
        else:
            pathsAndCounts[p] += 1
    print("Uniqe paths collected ------------")
    return pathsAndCounts

######## unique errors ########
def ErrorRepeatCheck():
    uniqueErrors = []
    #b. Handeling Duplicated Errors in attributes and tags
    for err in errors:
        if err not in uniqueErrors:
            uniqueErrors.append(err)
        else:
            continue

    print("Unique errors collected ------------")
    return uniqueErrors

######## write to csv ########
def toCSV(allPaths, allErrors, arg):
#Output to csv separate function
    xml_paths = {   
        "Repeated": [],
        "errors": [],
        "XMLPath": [] 
    }

    ## WRITING 'COUNTER', 'DUPLICATIONS' TO COLUMNS ##
    for k,v in allPaths.items():
        xml_paths["Repeated"].append(v)
        xml_paths["XMLPath"].append(k)

    ## WRITING 'ERRORS' TO A COLUMN ACCORDING TO EACH ROW IN xml_paths ##
    for xmls in xml_paths['XMLPath']:
        x = []
        for errs in allErrors:
            if errs in xmls:
                x.append(errs)
        xml_paths['errors'].append(", ".join(xs for xs in x))

    ## WRITE XML PATHS, ERROR REPORT TO CSV
    DF = pd.DataFrame(xml_paths)
    sorted = DF.sort_values("Repeated", ascending=False)
    sorted.to_csv("{}.csv".format(arg.output_directory), index=False)
    print("A csv file containing unique LDL xml paths, saved in this directory: {directory}.csv".format(directory = arg))

    ## TEST:
    print(len(xml_paths['XMLPath']))
    print(len(xml_paths['errors']))
    print(xml_paths['errors'])
    print("Number of all xml Paths ------------------------------ {}".format(len(paths)))
    print("Number of all Unique Paths ------------------------------{}".format(len(allPaths)))

######################## Final Run: Get Attributes and Tag list | Get xml Paths | Found errors with comparing attribute & tags with xml paths  ########################
def main():
    args = process_command_line_arguments()
    if args.input_directory and args.output_attribsTags:
    # Run the function to get and write the unique tags and attributes (-i,-oat)
        sourceMODs = MODs(args)
        getAttributeTags = MOD_Parse(sourceMODs)
        GetUniques = unique_tag_attrib()
        attribTags2csv = dataToCsv(args)

    elif args.input_directory and args.output_directory and args.input_csv:
    # Run the function to get XML paths, check for errors, and write to CSV (-i,-o,-c)
        sourceMODs = MODs(args)
        imputcsv = inpute_attribs_tags(args)
        parseTo = parseAll(sourceMODs,imputcsv)
        getUniquesPaths = PathRepeatCheck(parseTo)
        getUniqueErrors = ErrorRepeatCheck()
        writeToCSV = toCSV(getUniquesPaths, getUniqueErrors, args)
main()
# Latest Run Command>>> python3 The\ Parser6.py -i Data/TheParser_Test/Source -c Output/testMay15th.csv -o Output/TestMay16th 
