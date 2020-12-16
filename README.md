# xml2df
Convert XML file to a pandas dataframe. This package flattens the XML structure and creates a list of dictionaries that is then transformed to a dataframe.

requirement: pandas

The code is available in the xml2df.py
Running the file will allow you to process the example.xml file:

def main():
    document = ET.parse("example.xml")
    
    # batched elements is a list containing all the nodes who's children are of the same instance

    batched_elements = ["publish_date", "author_details"]
 
    df_result = xml2df(document, "book", batched_elements)
    print(df_result.head(5))
    
The file contains several functions to process your XML file. Please find the descriptions below:

xml2df function:

    This function runs the xml_flatten function to supply us with a flat structure result, the result of the xml_flatten function is then
        modified to join all existing lists to strings. If you do not need this final modification, please consider using the xml_flatten
        function instead which takes the same arguments.
    xml_document: the xml document to be processed
    root_node: specify the root node to begin drilldown
    batched_elements: as described in info allows you to identify batched nodes. For batched nodes, the xml.text is requested for all its
        child nodes. If any child nodes have their own children, this function will iter over all children and get their texts as well.
        Please note that when a the children have their own child node, they will ALSO be treated as a regular node and get their own values
        in a separate column.
        example:
            <book>
                <publication_date version="1">
                    <year>2020</year>
                    <month>05</month>
                    <day>11</day>
                </publication_date>
                <publication_date version="2">
                    <year>2020</year>
                    <month>05</month>
                    <day>11</day>
                </publication_date>
                <author>
                    John Doe
                </author>
            </book>
            To keep the subinstances of publication date as a whole, "publication_date" must be added to the batched_elements list
            leave empty if you don't need this
    unique_results: default set to True, set  to False if you need to get all results and not only unique results (applies set function)
    join_separator: default set to ";". modify this if you want the lists to be joined with any other separator


xml_flatten function:

    This function, given the root node, will drill down the elements and flatten the xml.
    xml_document: the xml document to be processed
    root_node: specify the root node to begin drilldown
    batched_elements: as described in info allows you to identify batched nodes. For batched nodes, the xml.text is requested for all its
        child nodes. If any child nodes have their own children, this function will iter over all children and get their texts as well.
        Please note that when a the children have their own child node, they will ALSO be treated as a regular node and get their own values
        in a separate column


get_flat_children function:

    This function will simply iterate over every node until there are no child nodes found. At this point the function will
        create a dictionary that saves the value of the node text along with the full attribute (name=value).
        format is then {"nodeparent_nodechild": "attribute_name=attribute_value|node_text"}. 
        Please note that only attributes belonging to the leaves (nodes without children) is retrieved. in case of batched 
        elements the attributes of the batch node are retrieved.
    batched_elements: please refer to the full explanation in xml2df function.
    result_dict: dictionary to aggregates the results.
    root: initially, the value supplied will be used to start the drilldown. when this function calls itself, the root will be changed
        to its children.
    prev_root: default set to empty string. do not modify unless you want all column names to start with a given string.
    attribute_separator: default set to "|". This separator is used to explicitly distinguish attributes from values in the final string.
    batch_result_separator: default set to " - ". This value can be modified to change the join string on the batched results.
