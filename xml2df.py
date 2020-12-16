import xml.etree.ElementTree as ET
import pandas as pd
 
def get_flat_children(batched_elements, result_dict, root, prev_root="", attribute_separator="|", batch_result_separator=" - "):
    """
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
    """
    # typically starting without the result dict, initiate here on first run
    if result_dict is None:
        result_dict = dict()
    root_tag = root.tag
    # if the current node contains children, start processing
    if list(root):
        # check if this node is been added to the batched elements
        batched = False
        for be in batched_elements:
            if root_tag == be:
                batched = True
        # if so, start retrieving the attributes and node text
        if batched:
            batch_result = list()
            attrib_values = ", ".join([a+"="+root.attrib.get(a) for a in root.attrib.keys()])
            for el in list(root):
                # if child node does not have own child nodes
                if len(list(el)) < 1:
                    # simply retrieve the text
                    batch_result.append(el.text)
                else:
                    # otherwise, the nodes are treated in a normal way (will receive their own column and values)
                    get_flat_children(batched_elements, result_dict, el, prev_root + "_" + root_tag)
                    # but the text within all the child nodes will also be added to the aggregated batched node
                    batch_result.extend([childnode.text.strip() for childnode in el.iter() if childnode.text != None])
            # join the list items into a string using the separator
            batch_result = batch_result_separator.join([x.strip() for x in batch_result if x != None])
            # add the attributes of the batch node if there is a attribute available
            if attrib_values.strip() != "":
                result_dict.setdefault(prev_root + "_" + root_tag, []).append(attrib_values + attribute_separator + batch_result)
            else:
                result_dict.setdefault(prev_root + "_" + root_tag, []).append(batch_result) 
        # if the node is not in the batched_elements list, process it by drilling down
        else:
            # for every child element
            for el in list(root):
                # drilldown and maintain the knowledge of the xml parents in the prev_root variable if not empty
                if prev_root != "":
                    get_flat_children(batched_elements, result_dict, el, prev_root + "_" + root_tag)
                else:
                    get_flat_children(batched_elements, result_dict, el, root_tag)
    # if there are no child nodes, retrieve the value and attributes
    else:
        attrib_values = ", ".join([a+"="+root.attrib.get(a) for a in root.attrib.keys()])
        if root.text:
            root_text = root.text.strip()
        else:
            root_text = ""
        if attrib_values.strip() != "":
            result_dict.setdefault(prev_root + "_" + root_tag, []).append(attrib_values + attribute_separator + root_text)
        else:
            result_dict.setdefault(prev_root + "_" + root_tag, []).append(root_text)
    # finally this function can return a result_dict with all the data stored into a single dictionary
    return result_dict
            
 
def xml_flatten(xml_document, root_node, batched_elements):
    """
    This function, given the root node, will drill down the elements and flatten the xml.
    xml_document: the xml document to be processed
    root_node: specify the root node to begin drilldown
    batched_elements: as described in info allows you to identify batched nodes. For batched nodes, the xml.text is requested for all its
        child nodes. If any child nodes have their own children, this function will iter over all children and get their texts as well.
        Please note that when a the children have their own child node, they will ALSO be treated as a regular node and get their own values
        in a separate column
    """
    results = list()
    for item in xml_document.iterfind(root_node):
        result_dict = get_flat_children(batched_elements, None, item)
        results.append(result_dict)
    return results

def xml2df(xml_document, root_node, batched_elements, unique_results=True, join_separator=";"):
    """
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
    """
    results = xml_flatten(xml_document, root_node, batched_elements)

    if unique_results:
        for _row in results:
            for key, val in _row.items():
                if isinstance(val, list):
                    _row[key] = join_separator.join(list(set(val)))
    else:
        for _row in results:
            for key, val in _row.items():
                if isinstance(val, list):
                    _row[key] = join_separator.join(val)
    print(results)
    return pd.DataFrame(results)

