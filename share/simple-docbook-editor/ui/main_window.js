var doc_structure_closed_nodes = new Array();
var selected_doc_section = null;
var edited_section_id = 0;
var saveTimeout = null;

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
        if (selected_doc_section){
            node = jQuery("#doc_structure").tree("getNodeById", selected_doc_section);
            jQuery("#doc_structure").tree('selectNode', node);
        }
        for (var i in doc_structure_closed_nodes){
            node = jQuery("#doc_structure").tree("getNodeById", doc_structure_closed_nodes[i]);
            if (node){
                jQuery("#doc_structure").tree('closeNode', node);
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
    edited_section_id = edit_data.section_id;
    selected_doc_section = edit_data.section_id;
    tinymce.get("tinymcecontainer").setContent(edit_data.html);
    update_editor_height();
}

function update_editor_height(){
    jQuery("#tinymcecontainer_ifr").css("height", (jQuery("#editor_inside_wrapper").height() - jQuery("#tinymcecontainer_ifr").offset().top) + "px");
}

function refresh_view_for_new_book(section_id)
{
    tinymce.get("tinymcecontainer").setContent("");
    doc_structure_closed_nodes = new Array();
    selected_doc_section = section_id;
    edited_section_id = 0;
    reload_doc_structure();
}


function save_editor_contents()
{
    if (saveTimeout)
    {
        clearTimeout(saveTimeout);
    }
    saveTimeout = setTimeout(function()
    {
        if (edited_section_id)
        {
            alert('set_section_contents:' + edited_section_id + ':' + tinymce.get("tinymcecontainer").getContent());
        }
    }, 300);
}

jQuery(document).ready(function()
{
    jQuery('#doc_structure').tree({
        data: [],
        autoOpen: true,
        dragAndDrop: false,
        onCanSelectNode: function(node)
        {
            return (node.edit_mode != null);
        }
    });
    jQuery("#doc_structure").bind('tree.select', function(event){
        if (event.node.id != edited_section_id)
        {
            selected_doc_section = event.node.id;
            load_doc_section(event.node.id);
        }
    });
    jQuery("#doc_structure").bind('tree.open', function(event){
        var i = doc_structure_closed_nodes.indexOf(event.node.id);
        while (i != -1){
            doc_structure_closed_nodes.splice(i, 1);
            i = doc_structure_closed_nodes.indexOf(event.node.id);
        }
    });
    jQuery("#doc_structure").bind('tree.close', function(event){
        doc_structure_closed_nodes.push(event.node.id);
    });
    
    jQuery("#leftbar").resizable({
        handles: "e",
        resize: function(event, ui){
            jQuery("#editor_wrapper").css("left", jQuery("#leftbar").outerWidth());
        }
    });
    
    tinymce.init({
        selector: "#tinymcecontainer",
        setup: function(editor){
            editor.on('change', function(e){
                save_editor_contents();
            });
            editor.on('init', function(e){
                tinymce.get("tinymcecontainer").getBody().onkeyup = function(event)
                {
                    save_editor_contents();
                }
                setTimeout(function(){
                    update_editor_height();
                    alert("editor_ready");
                }, 100);
            });
        },
        menubar: false,
        statusbar: false,
        plugins: ["code image noneditable"],
        toolbar: "bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | formatselect fontselect fontsizeselect | cut copy paste | bullist numlist | outdent indent | blockquote | undo redo | removeformat subscript superscript | image | code",
        relative_urls: false,
        content_style: (
            'div.sect1,div.sect2,div.sect3 {background-color: #B3B3B3;}' +
            'div.sect1:before {content: "sect1"}' +
            'div.sect2:before {content: "sect2"}' +
            'div.sect3:before {content: "sect3"}'
        ),
        object_resizing: "img,table"
    });
    
    jQuery(window).resize(function(event){
        update_editor_height();
    });
});
