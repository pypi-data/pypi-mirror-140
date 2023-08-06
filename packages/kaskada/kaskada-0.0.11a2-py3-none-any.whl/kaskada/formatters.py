"""
Copyright (C) 2022 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from datetime import datetime
from tabnanny import verbose

from attr import has
from domonic.ext.html5lib_ import getTreeBuilder
from domonic.html import a, b, button, div, pre, script, style, table, td, th, tr
from domonic.utils import Utils
import html5lib
import inspect
import io
import pandas
import pkg_resources
import pprint
import re
import sys


import kaskada.fenl.v1alpha as kaskada_fenl_pb2

kaskada_fenl_primitive_types = {
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_BOOL: "bool",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_MICROSECOND: "duration_us",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_MILLISECOND: "duration_ms",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_NANOSECOND: "duration_ns",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_DURATION_SECOND: "duration_s",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F16: "f16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F32: "f32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_F64: "f64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I16: "i16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I32: "i32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I64: "i64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_I8: "i8",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_INTERVAL_DAY_TIME: "interval_days",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_INTERVAL_YEAR_MONTH: "interval_months",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_NULL: "null",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_STRING: "string",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_MICROSECOND: "timestamp_us",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_MILLISECOND: "timestamp_ms",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_NANOSECOND: "timestamp_ns",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_TIMESTAMP_SECOND: "timestamp_s",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U16: "u16",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U32: "u32",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U64: "u64",
    kaskada_fenl_pb2.schema_pb2.DataType.PRIMITIVE_TYPE_U8: "u8",
}

def convert_fenl_schema_field(field):
    """
    Converts a fenl field to a string representation.

    Args:
        field (kaskada_fenl_pb2.schema_pb2.Schema_Field) : the input field

    Returns:
        str: The string representation of the fenl Field
    """
    return field.name, convert_fenl_datatype(field.data_type)

def convert_fenl_datatype(data_type):
    """
    Converts a fenl dataType to a string representation.

    Args:
        data_type (kaskada_fenl_pb2.schema_pb2.DataType) : the input dataType

    Returns:
        str: The string representation of the fenl DataType
    """
    type_string = None
    if data_type.HasField("primitive"):
        type_string = kaskada_fenl_primitive_types.get(data_type.primitive, "<unknown>")
    elif data_type.HasField("struct"):
        type_string = "<struct>"
    elif data_type.HasField("window"):
        type_string = "<window>"
    return type_string

def get_classname(obj):
    return f"{obj.__module__}.{obj.__name__}"

def get_schema_dataframe(obj):
    """
    Gets a dataframe from a schema object if it exists

    Args:
        obj (kaskada.fenl.v1alpha.schema_pb2.Schema | Any): Either a schema object or an object that has a schema object at the root level

    Returns:
        pandas.dataframe | None: Either a dataframe describing the schemea or None if no schema exists in the passed object.
    """
    if hasattr(obj, "schema"):
        obj = obj.schema

    if (not hasattr(obj, "fields")) or len(obj.fields) == 0:
        return None
    fields = {}
    for idx, field in enumerate(obj.fields):
        name, typeString = convert_fenl_schema_field(field)
        fields[idx] = [name, typeString]
    return pandas.DataFrame.from_dict(data=fields, orient="index", columns=["column_name", "column_type"])

def get_datetime(pb2_timestamp):
    """
    Converts a google.protobuf.timestamp_pb2 into a python datetime object.

    Args:
        pb2_timestamp (google.protobuf.timestamp_pb2): The protobuf timestamp.

    Returns:
        datetime: The python datetime.
    """
    return datetime.fromtimestamp(pb2_timestamp.seconds + pb2_timestamp.nanos/1e9)

def get_properties(obj):
    """
    Converts a protobuf response into a simple python dictionary.

    Args:
        obj (Any): A deserialized protobuf object.

    Returns:
        dict of {str : Any}: A nested set of keys and values with structure matching the protobuf input.
    """
    results = {}
    for propName in dir(obj):
        if re.search(r"^[a-z]", propName) is None:
            continue
        propVal = getattr(obj,propName)
        propType = type(propVal)
        prop_class = get_classname(propType)
        if propType.__name__ in ("method"):
            continue
        elif propType in (int, float, bool):
            results[propName] = propVal
        elif propType is str:
            if propVal != "":
                results[propName] = propVal
        elif prop_class == "google.protobuf.pyext._message.RepeatedCompositeContainer":
            if len(propVal) > 0:
                results[propName] = [get_properties(subObj) for subObj in propVal]
        elif prop_class == "google.protobuf.timestamp_pb2.Timestamp":
            results[propName] = get_datetime(propVal).isoformat()
        elif prop_class.startswith("pandas."):
            results[propName] = propVal
        else:
            results[propName] = get_properties(propVal)
    return results

def get_item(obj, keys, default = ""):
    """
    Safely recursively gets an item from a dict, otherwise returns the default value

    Args:
        obj (dict of {str : Any}): Dictionary of (nested) key item pairs
        keys (list of str): The list of keys use to navigate to the desired item in the dictionary.
        default (str, optional): The default value to return if the item isn't found. Defaults to "".

    Returns:
        string: Either the found value or the default.
    """
    while (len(keys) > 0):
        key = keys.pop(0)
        if key in obj:
            obj = obj[key]
        else:
            return default
    return obj

def appendChildIfNotNone(parent, child):
    if child is not None:
        parent.appendChild(child)

def appendChildren(parent, children):
    for child in children:
        appendChildIfNotNone(parent, child)

def html_obj_table_row(key, value):
    """
    Returns a html table row, where the key is bolded, and the value is output as code.
    """
    if value is None or value == "":
        return None
    return tr(td(b(key)),td(pre(value)))

def html_table_row(key, value):
    """
    Returns a html table row, where the key is bolded, and the value is output as is.
    """
    return tr(td(b(key)),td(value))

def get_request_details_table_row_if_exists(props):
    if "request_details" in props:
        request_details = props.pop("request_details")
        nested_table = table(html_obj_table_row("request_id", get_item(request_details, ["request_id"])), _class="kda_table")
        return html_table_row("request_details", nested_table)
    return None

def html_obj_id_row(index, obj, props):
    obj_type = type(obj).__name__.lower()
    obj_name_key = f"{obj_type}_name"
    obj_name = get_item(props, [obj_name_key])
    return tr(td(pre(index)),td(pre(obj_name)))

def get_shared_generic_response_props_and_schema_dataframe(obj):
    props = get_properties(obj)
    props.pop("file_count", "") # remove table `file_count` since it isn't populated yet
    schema_df = None
    # special handling of `result_type` for views
    if hasattr(obj, "result_type"):
        fenl_datatype = convert_fenl_datatype(obj.result_type)
        if fenl_datatype is None:
            props.pop("result_type","") #remove `result_type` from props
        else:
            props["result_type"] = Utils.escape(fenl_datatype)
            if obj.result_type.HasField("struct"):
                schema_df = get_schema_dataframe(obj.result_type.struct)
                if schema_df is not None:
                    props["result_type"] += " (see Schema tab)" 

    # remove schema from details view, put in schema viewer instead
    if hasattr(obj, "schema"):
        props.pop("schema", "")
        schema_df = get_schema_dataframe(obj)
        if schema_df is not None:
            props["schema"] = "(see Schema tab)" 

    return props, schema_df

def get_shared_generic_response_table_rows(obj, props):
    obj_type = type(obj).__name__.lower()

    # try to pop off obj_id and obj_name first
    obj_id_key = f"{obj_type}_id"
    obj_id = props.pop(obj_id_key, None)
    obj_name_key = f"{obj_type}_name"
    obj_name = props.pop(obj_name_key, None)

    # also remove create & update time, and slice info from props
    create_time = props.pop("create_time", None)
    update_time = props.pop("update_time", None)
    props.pop("slice", None)

    rows = [
        # first row is item name
        html_obj_table_row(obj_name_key, obj_name),
        # stop showing item ids since they aren't actionable by the user
        # html_obj_table_row(obj_id_key, obj_id),
    ]

    # add remainder of fields
    for key in props:
        rows.append(html_obj_table_row(key, props[key]))

    # special handling for slice configs
    if hasattr(obj, "slice"):
        rows.append(html_table_row("slice", slice_request_table(obj.slice)))
    
    # add create & update time at the end
    rows.append(html_obj_table_row("create_time", create_time))
    rows.append(html_obj_table_row("update_time", update_time))

    return rows

def generic_response_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    
    # geneneric responses should contain 2 properties at the root level
    # request_details and the actual object
    props = get_properties(obj)
    details = table(_class="kda_table")

    # pull off request_details
    request_details = get_request_details_table_row_if_exists(props)

    # pull of analysis
    errors = None
    can_execute = None
    analysis_props = props.pop("analysis", None)
    if analysis_props is not None:
        can_execute, nested_details, errors = analysis_and_errors_tables(obj.analysis)
        details.appendChild(html_table_row("analysis", nested_details))

    schema_df = None
    if can_execute is not False:
        # expect that only the actual object is left
        if len(props) == 1 and type(props[list(props)[0]]) not in (int, float, bool, str):
            obj_key = list(props)[0]
            actual_obj = getattr(obj, obj_key)
            
            actual_props, schema_df = get_shared_generic_response_props_and_schema_dataframe(actual_obj)
            if len(actual_props) > 0:
                nested_table = table(_class="kda_table")
                appendChildren(nested_table, get_shared_generic_response_table_rows(actual_obj, actual_props))
                details.appendChild(html_table_row(obj_key, nested_table))
        else:
            appendChildren(details, get_shared_generic_response_table_rows(obj, props))

    schema = convert_df_to_domonic(schema_df) if schema_df is not None else None 
    appendChildIfNotNone(details, request_details)

    title_to_set_active = "Details" if errors is None else "Errors"
    return str(tab_panel([("Details", details), ("Schema", schema), ("Errors", errors), ("Raw", pre(pprint.pformat(obj)))],title_to_set_active=title_to_set_active))

def generic_object_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    
    props, schema_df = get_shared_generic_response_props_and_schema_dataframe(obj)
    schema = convert_df_to_domonic(schema_df) if schema_df is not None else None

    details = table(_class="kda_table")
    appendChildren(details, get_shared_generic_response_table_rows(obj, props))

    return str(tab_panel([("Details", details), ("Schema", schema), ("Raw", pre(pprint.pformat(obj)))]))

def schema_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()

    schema_df = get_schema_dataframe(obj)
    schema = convert_df_to_domonic(schema_df) if schema_df is not None else None

    return str(tab_panel([("Schema", schema), ("Raw", pre(pprint.pformat(obj)))]))

def data_type_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()

    title_to_set_active = ""
    result_type = Utils.escape(convert_fenl_datatype(obj))
    schema_df = None
    if obj.HasField("struct"):
        schema_df = get_schema_dataframe(obj.struct)
        if schema_df is not None:
            result_type += " (see Schema tab)"
            title_to_set_active = "Schema"
    
    schema = convert_df_to_domonic(schema_df) if schema_df is not None else None

    return str(tab_panel([("Result Type", pre(result_type)), ("Schema", schema), ("Raw", pre(pprint.pformat(obj)))], title_to_set_active))

def response_delete_html_formatter(del_resp):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    
    request_details = get_request_details_table_row_if_exists(get_properties(del_resp))

    del_resp_type = type(del_resp).__name__
    del_obj = del_resp_type.replace("Response", "")
    
    details = table(_class="kda_table")
    details.appendChild(html_obj_table_row(del_obj, "success"))
    details.appendChild(request_details)

    return str(tab_panel([("Details", details), ("Raw", pre(pprint.pformat(del_resp)))]))

def response_list_html_formatter(list_resp):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    props = get_properties(list_resp)

    request_details = get_request_details_table_row_if_exists(props)

    list_resp_type = type(list_resp).__name__
    list_key = list_resp_type.replace("Response", "").replace("List", "").lower()

    details = table(_class="kda_table")
    
    # after pulling the request_id, only the item list should remain
    if len(props) == 1:
        list_value = getattr(list_resp, list_key)
        list_props = props[list_key]
        list_type = type(list_value)
        nested_table = table(_class="kda_table")
        details.appendChild(html_table_row(list_key, nested_table))
        nested_table.appendChild(tr(th("index"),th("name")))
        
        if get_classname(list_type) == "google.protobuf.pyext._message.RepeatedCompositeContainer":
            for i in range(len(list_value)):
                appendChildIfNotNone(nested_table, html_obj_id_row(str(i), list_value[i], list_props[i]))
    else: # when list is empty
        details.appendChild(html_table_row(list_key, Utils.escape("<empty>")))

    
    appendChildIfNotNone(details, request_details)

    return str(tab_panel([("Details", details), ("Raw", pre(pprint.pformat(list_resp)))]))

def proto_list_html_formatter(list_resp):
    item_count = len(list_resp)
    if item_count == 0:
        return str(pre(pprint.pformat(list_resp)))

    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    details = table(_class="kda_table")

    # peek at the type of items in the list
    item_class = get_classname(type(list_resp[0]))

    if item_class == "kaskada.errdetails.v1alpha.fenl_diagnostics_pb2.FenlDiagnostic":
        for i in range(item_count):
            fenl_diag = list_resp[i]
            details.appendChild(html_obj_table_row(i, fenl_diag.formatted))
    else:
        details.appendChild(tr(th("index"),th("name")))
        for i in range(item_count):
            appendChildIfNotNone(details, html_obj_id_row(i, list_resp[i], get_properties(list_resp[i])))

    return str(tab_panel([("Details", details), ("Raw", pre(pprint.pformat(list_resp)))]))

def slice_request_table(obj):
    details = table(_class="kda_table")
    if obj.HasField("percent"):
        details.appendChild(html_obj_table_row("percent", obj.percent.percent))
    else:
        details.appendChild(html_obj_table_row("None", "(full dataset used for query)"))
    return details

def slice_request_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    return str(tab_panel([("Details", slice_request_table(obj)), ("Raw", pre(pprint.pformat(obj)))]))

def get_shared_query_response_content(resp_obj):
    props = get_properties(resp_obj)
    parquet_path = get_item(props, ["parquet", "path"])
    redis_bulk_path = get_item(props, ["redis_bulk", "path"])

    resultsExist = False
    details = table(_class="kda_table")
    if parquet_path != "":
        nested_table = table(html_table_row("path",a(parquet_path, _href=parquet_path)), _class="kda_table")
        details.appendChild(html_table_row("parquet", nested_table))
        resultsExist = True
    elif redis_bulk_path != "":
        nested_table = table(html_table_row("path",a(redis_bulk_path, _href=redis_bulk_path)), _class="kda_table")
        details.appendChild(html_table_row("redis_bulk", nested_table))
        resultsExist = True
    else:
        nested_table = table(html_obj_table_row("can_execute", get_item(props, ["analysis", "can_execute"])), _class="kda_table")
        details.appendChild(html_table_row('analysis', nested_table))

    if resultsExist:
        details.appendChild(html_table_row("slice", slice_request_table(resp_obj.slice)))

    schema = None
    schema_df = get_schema_dataframe(resp_obj)
    if schema_df is not None:
        schema = convert_df_to_domonic(schema_df)
        details.appendChild(html_obj_table_row("schema", "(see Schema tab)"))

    rows = [
        html_obj_table_row("data_token_id", get_item(props, ["data_token_id"])),
        html_obj_table_row("next_resume_token", get_item(props, ["next_resume_token"])),
        get_request_details_table_row_if_exists(props),
    ]
    appendChildren(details, rows)

    return { "Details": details, "Schema": schema}

def query_response_html_formatter(resp_obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    
    content = get_shared_query_response_content(resp_obj)

    return str(tab_panel([("Details", content["Details"]), ("Schema", content["Schema"]), ("Raw", pre(pprint.pformat(resp_obj)))]))

def fenlmagic_query_result_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()

    content = get_shared_query_response_content(obj.query_response)
    details_table = content["Details"]
    details_table.appendChild(html_obj_table_row("query", obj.query))

    raw = {
        "query": obj.query,
        "query_response": obj.query_response,
    }

    dataframe = None
    if obj.dataframe is not None:
        buffer = io.StringIO()
        obj.dataframe.info(buf=buffer, verbose=False)
        raw["dataframe"] = buffer.getvalue().replace("<class 'pandas.core.frame.DataFrame'>\n","")
        dataframe = convert_df_to_domonic(obj.dataframe, 10, True)

    return str(tab_panel([("Dataframe", dataframe), ("Details", content["Details"]), ("Schema", content["Schema"]), ("Raw", pre(pprint.pformat(raw).replace("\\n","")))]))

def entity_filter_html_formatter(obj):
    props = get_properties(obj)
    details = table(_class="kda_table")
    filter_type = type(obj).__name__
    if filter_type == "EntityPercentFilter":
        details.appendChild(html_obj_table_row("percent", obj.percent))

    return str(tab_panel([("Details", details), ("Raw", pre(pprint.pformat(props).replace("\\n","")))]))

def analysis_and_errors_tables(obj):
    details = table(html_obj_table_row("can_execute", str(obj.can_execute)), _class="kda_table")
    errors = None
    if not obj.can_execute:
        details.appendChild(html_obj_table_row("fenl_diagnostics", "(see Errors tab)"))
        errors = fenl_diagnostics_table(obj.fenl_diagnostics)
    return obj.can_execute, details, errors

def analysis_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    can_execute, details, errors = analysis_and_errors_tables(obj)
    title_to_set_active = "Details" if errors is None else "Errors"
    return str(tab_panel([("Details", details), ("Errors", errors), ("Raw", pre(pprint.pformat(obj)))], title_to_set_active=title_to_set_active))

def fenl_diagnostics_table(obj):
    details = table(_class="kda_table")
    for i in range(len(obj.fenl_diagnostics)):
        fenl_diag = obj.fenl_diagnostics[i]
        details.appendChild(html_obj_table_row(i, fenl_diag.formatted))
    return details

def fenl_diagnostics_html_formatter(obj):
    output_custom_css_and_javascript_if_output_wrapped_in_iframe()
    details = table(html_table_row("fenl_diagnostics", fenl_diagnostics_table(obj)))
    return str(tab_panel([("Details", details), ("Raw", pre(pprint.pformat(obj)))]))

def convert_df_to_domonic(df, max_rows = None, show_dimensions = False):
    parser = html5lib.HTMLParser(tree=getTreeBuilder())
    return parser.parse(df.to_html(max_rows=max_rows, notebook=True, show_dimensions=show_dimensions))
        
def tab_panel(content_list, title_to_set_active = ""):
    """
    Creates a tab-panel for the passed content list.

    Args:
        content_list (list of tuple of (str, Any)): A list of tuples, where the the first value 
        in the tuple is the tab title, and the second is the tab contents.
        
        title_to_set_active str: The name of the tab title to set active when the panel loads. If 
        unset, the first tab will be set active.

    Returns:
        domonic.html.div: A div html element wrapping the tabs and content.  Pass this value to 
        str() to get the string html output.
    """
    if len(content_list) == 0:
        return None

    tab_links = div(_class="kda_tab")
    root_div = div(tab_links)

    for titleContent in content_list:
        title = titleContent[0]
        content = titleContent[1]
        if content is None:
            continue
        if title_to_set_active == "":
            title_to_set_active = title
        lower_title = title.lower()

        tab_button_class = "kda_tablinks kda_active" if title_to_set_active == title else "kda_tablinks"
        tab_links.appendChild(button(title, _class=tab_button_class, _onclick=f"openTab(event, '{lower_title}')"))

        scroll_div = div(_class="kda_scroll_container").html(content)
        content_div = div(_class=f"{lower_title} kda_tabcontent").html(scroll_div)
        content_div.style.display = "block" if title_to_set_active == title else "none"
        root_div.appendChild(content_div)

    return root_div

def output_custom_css_and_javascript():
    """
    Outputs our custom css and javascript to the current cell
    """
    import IPython
    css = pkg_resources.resource_string(__name__, "formatters.css").decode("utf-8")
    js = pkg_resources.resource_string(__name__, "formatters.js").decode("utf-8")
    IPython.core.display.display(IPython.core.display.HTML(str(style(css))))
    IPython.core.display.display(IPython.core.display.HTML(str(script(js, _type="text/javascript"))))

def cell_output_is_wrapped_in_iframe():
    """
    Based on the environment that the code is running inside of, the cell output may be  
    automatically wrapped in an iFrame.  
    For example, in google colab: "the output of each cell is hosted in a separate iframe 
    sandbox with limited access to the global notebook environment"
    In enviroments like these, we need to include our custom css & javascript in every output.

    Returns:
        bool: True if the environment will automatically wrap the cell output in an iFrame, otherwise False.
    """
    if "google.colab" in str(get_ipython()):
        return True
    else:
        return False


def output_custom_css_and_javascript_if_output_wrapped_in_iframe():
    """
    Outputs our custom css and javascript to the cell ouput if the output for the cell
    will be wrapped in an iFrame.  (i.e. in google colab)
    """
    if cell_output_is_wrapped_in_iframe():
        output_custom_css_and_javascript()

def try_init():
    try:
        # the following command will throw an exception in non-iPython environments
        html_formatter = get_ipython().display_formatter.formatters["text/html"]

        # dynamically assign formatters to kaskada protobuf types
        mods = sys.modules.copy()
        for key in mods:
            if key.endswith("_grpc"):
                continue
            if key.startswith("kaskada."):
                for cls in inspect.getmembers(mods[key], inspect.isclass):
                    classname = get_classname(cls[1])
                    if classname == "kaskada.api.v1alpha.compute_pb2.QueryResponse":
                        html_formatter.for_type(classname, query_response_html_formatter) # kda_table formatter for QueryResponse
                    elif classname == "kaskada.fenl.v1alpha.schema_pb2.Schema":
                        html_formatter.for_type(classname, schema_html_formatter) 
                    elif classname == "kaskada.fenl.v1alpha.schema_pb2.DataType":
                        html_formatter.for_type(classname, data_type_html_formatter)
                    elif classname == "kaskada.prepare.v1alpha.slice_pb2.SliceRequest":
                        html_formatter.for_type(classname, slice_request_html_formatter)
                    elif classname == "kaskada.errdetails.v1alpha.fenl_diagnostics_pb2.FenlDiagnostics":
                        html_formatter.for_type(classname, fenl_diagnostics_html_formatter)
                    elif classname == "kaskada.api.v1alpha.shared_pb2.Analysis":
                        html_formatter.for_type(classname, analysis_html_formatter)
                    elif "Delete" in classname and "Response" in classname:
                        html_formatter.for_type(classname, response_delete_html_formatter) # generic formatter for Delete responses
                    elif "List" in classname and "Response" in classname:
                        html_formatter.for_type(classname, response_list_html_formatter) # generic formatter for List responses
                    elif "Response" in classname:
                        html_formatter.for_type(classname, generic_response_html_formatter) # generic formatter for other responses
                    else:
                        html_formatter.for_type(classname, generic_object_html_formatter) # generic formatter for all other objects
        
        # the following types don't normally exist when the library first loads
        html_formatter.for_type("kaskada.materialization.MaterializationView", generic_object_html_formatter)
        html_formatter.for_type("kaskada.materialization.RedisAIDestination", generic_object_html_formatter)
        html_formatter.for_type("kaskada.compute.EntityPercentFilter", entity_filter_html_formatter)
        html_formatter.for_type("fenlmagic.QueryResult", fenlmagic_query_result_html_formatter)

        # additional non-kaskada types we want to assign formatters to
        html_formatter.for_type("google.protobuf.pyext._message.RepeatedCompositeContainer", proto_list_html_formatter)

        if not cell_output_is_wrapped_in_iframe():
            # load our custom css into the page
            output_custom_css_and_javascript()

    except:
        pass
