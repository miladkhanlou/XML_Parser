# XML Parser
A tool for parsing Louisiana Digital Library XML files as one of our ETL pipelines.
</br>
On commandline we can tell the code accomplish each of the following tasks separately:</br>

a. Parses into a source of LSU MODs (in the form of xml) and gets the data bellow and put them into a csv as a source of correct and all the tags and attributes in that collection of content:</br>

  i. all the unique attributes in xml</br>

  ii. all the unique tags</br>

  iii. gets the number of times attributes and tags where duplicated</br>

b. Parses into a target destination and get the xml paths</br>

c. Compaire tags and attributes of the written XML paths with the list of tags and attributes from 'a' and if there were any new ones or misspelled one it will write that to a column called Error</br>

