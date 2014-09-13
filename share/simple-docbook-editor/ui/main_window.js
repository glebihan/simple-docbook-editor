var doc_structure_closed_nodes = new Array();
var selected_doc_section = null;
var edited_section_id = 0;
var edited_section_node = null;
var saveTimeout = null;
var sourceSaveTimeout = null;
var current_file_browser_window = null;
var source_editor = null;

function reload_doc_structure()
{
    alert("reload_doc_structure");
}

function set_doc_structure(doc_structure)
{
    if (doc_structure === null)
    {
        jQuery("#doc_structure").tree("loadData", []);
    }
    else
    {
        jQuery("#doc_structure").tree("loadData", [doc_structure]);
        if (selected_doc_section)
        {
            node = jQuery("#doc_structure").tree("getNodeById", selected_doc_section);
            jQuery("#doc_structure").tree('selectNode', node);
        }
        for (var i in doc_structure_closed_nodes)
        {
            node = jQuery("#doc_structure").tree("getNodeById", doc_structure_closed_nodes[i]);
            if (node)
            {
                jQuery("#doc_structure").tree('closeNode', node, false);
            }
        }
    }
}

function load_doc_section(section_id)
{
    if (saveTimeout)
    {
        clearTimeout(saveTimeout);
        saveTimeout = null;
    }
    alert("load_doc_section:" + section_id);
}

function set_edit_data(edit_data)
{
    if (edit_data.edit_mode == "html")
    {
        edited_section_node = jQuery(edit_data.html);
        tinymce.get("tinymcecontainer").setContent(edited_section_node.html());
    }
    edited_section_id = edit_data.section_id;
    selected_doc_section = edit_data.section_id;
    update_editor_height();
    source_editor.setValue(edit_data.xml);
}

function update_editor_height(){
    jQuery("#tinymcecontainer_ifr").css("height", (jQuery("#editor_inside_wrapper").height() - jQuery("#tinymcecontainer_ifr").offset().top) + "px");
    source_editor.setSize(null, jQuery("#editor_inside_wrapper").height() - jQuery("div.CodeMirror").offset().top);
}

function refresh_view_for_new_book(section_id)
{
    tinymce.get("tinymcecontainer").setContent("");
    doc_structure_closed_nodes = new Array();
    selected_doc_section = section_id;
    edited_section_id = 0;
    reload_doc_structure();
}

function do_save_editor_contents()
{
    edited_section_node.html(tinymce.get("tinymcecontainer").getContent());
    if (edited_section_id)
    {
        alert('set_section_contents:' + edited_section_id + ':' + edited_section_node[0].outerHTML);
    }
}

function save_editor_contents()
{
    if (saveTimeout)
    {
        clearTimeout(saveTimeout);
    }
    saveTimeout = setTimeout(do_save_editor_contents, 300);
}

function do_save_source_editor_contents()
{
    alert("set_section_source_contents:" + edited_section_id + ":" + source_editor.getValue());
}

function save_source_editor_contents()
{
    if (sourceSaveTimeout)
    {
        clearTimeout(sourceSaveTimeout);
    }
    sourceSaveTimeout = setTimeout(do_save_source_editor_contents, 300);
}

function set_file_browser_filename(data)
{
    current_file_browser_window.document.getElementById(data.field_name).value = data.url;
}

jQuery(document).ready(function()
{
    jQuery('#doc_structure').tree(
    {
        data: [],
        autoOpen: true,
        dragAndDrop: false,
        onCanSelectNode: function(node)
        {
            return (node.edit_mode != null);
        }
    });
    jQuery("#doc_structure").bind('tree.select', function(event)
    {
        if (event.node.id != edited_section_id)
        {
            selected_doc_section = event.node.id;
            load_doc_section(event.node.id);
        }
    });
    jQuery("#doc_structure").bind('tree.open', function(event)
    {
        var i = doc_structure_closed_nodes.indexOf(event.node.id);
        while (i != -1){
            doc_structure_closed_nodes.splice(i, 1);
            i = doc_structure_closed_nodes.indexOf(event.node.id);
        }
    });
    jQuery("#doc_structure").bind('tree.close', function(event)
    {
        doc_structure_closed_nodes.push(event.node.id);
    });
    
    jQuery("#leftbar").resizable(
    {
        handles: "e",
        resize: function(event, ui)
        {
            jQuery("#editor_wrapper").css("left", jQuery("#leftbar").outerWidth());
        }
    });
    
    tinymce.init(
    {
        selector: "#tinymcecontainer",
        setup: function(editor)
        {
            editor.on('click', function(e)
            {
                if (jQuery(e.target).hasClass("mceNonEditable") && jQuery(e.target).hasClass("subsection") && parseInt(jQuery(e.target).attr("data-section-id")) > 0)
                {
                    selected_doc_section = parseInt(jQuery(e.target).attr("data-section-id"));
                    load_doc_section(parseInt(jQuery(e.target).attr("data-section-id")));
                    reload_doc_structure();
                }
            });
            editor.on('change', function(e)
            {
                save_editor_contents();
            });
            editor.on('init', function(e)
            {
                tinymce.get("tinymcecontainer").getBody().onkeyup = function(event)
                {
                    save_editor_contents();
                }
                setTimeout(function()
                {
                    update_editor_height();
                    alert("editor_ready");
                }, 100);
            });
        },
        menubar: false,
        statusbar: false,
        plugins: ["code image noneditable docbook_subsections"],
        toolbar: "bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | formatselect fontselect fontsizeselect | cut copy paste | bullist numlist | outdent indent | blockquote | undo redo | removeformat subscript superscript | image | add_docbook_subsection | code",
        relative_urls: false,
        content_style: (
            'div.subsection {background-color: #B3B3B3; cursor: pointer; padding: 5px; margin-bottom: 10px;}'
        ),
        object_resizing: "img,table",
        file_browser_callback: function(field_name, url, type, win)
        {
            current_file_browser_window = win;
            if (type == "image")
            {
                alert("browse_image:" + field_name + ":" + url);
            }
        }
    });
    
    source_editor = CodeMirror.fromTextArea(document.getElementById("source_editor"),
    {
        mode: 'text/html',
        autoCloseTags: true,
        lineNumbers: true,
        indentUnit: 4
    });
    source_editor.on("change", function(editor, event)
    {
        save_source_editor_contents();
    });
    
    jQuery(window).resize(function(event)
    {
        update_editor_height();
    });
    
    jQuery("#maintabs").tabs(
    {
        activate: function(event)
        {
            update_editor_height();
            load_doc_section(edited_section_id);
        }
    });
});
