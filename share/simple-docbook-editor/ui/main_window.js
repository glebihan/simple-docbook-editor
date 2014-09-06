var doc_structure_closed_nodes = new Array();
var selected_doc_section = null;

function reload_doc_structure()
{
    alert("reload_doc_structure");
}

function set_doc_structure(doc_structure)
{
    jQuery("#doc_structure").tree("loadData", [doc_structure]);
    if (selected_doc_section){
        node = jQuery("#doc_structure").tree("getNodeById", selected_doc_section.id);
        jQuery("#doc_structure").tree('selectNode', node);
    }
    for (var i in doc_structure_closed_nodes){
        node = jQuery("#doc_structure").tree("getNodeById", doc_structure_closed_nodes[i]);
        if (node){
            jQuery("#doc_structure").tree('closeNode', node);
        }
    }
}

function load_doc_section(section_id)
{
    alert("load_doc_section:" + section_id);
}

function set_edit_data(edit_data)
{
    tinymce.get("tinymcecontainer").setContent(edit_data.html);
    update_editor_height();
}

function update_editor_height(){
    jQuery("#tinymcecontainer_ifr").css("height", (jQuery("#editor_inside_wrapper").height() - jQuery("#tinymcecontainer_ifr").offset().top) + "px");
}

function refresh_view_for_new_book()
{
    tinymce.get("tinymcecontainer").setContent("");
    doc_structure_closed_nodes = new Array();
    selected_doc_section = null;
    reload_doc_structure();
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
        selected_doc_section = event.node;
        load_doc_section(event.node.id);
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
    
    tinymce.init({
        selector: "#tinymcecontainer",
        setup: function(editor){
            editor.on('change', function(e){
                //alert('set_note_contents:' + editing_note_local_id + ':' + editor.getContent());
            });
            editor.on('init', function(e){
                setTimeout(function(){
                    update_editor_height();
                    alert("editor_ready");
                    //~ load_doc_section(40);
                }, 100);
            });
        },
        menubar: false,
        statusbar: false,
        toolbar: "bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | formatselect fontselect fontsizeselect | cut copy paste | bullist numlist | outdent indent | blockquote | undo redo | removeformat subscript superscript"
    });
    
    jQuery(window).resize(function(event){
        update_editor_height();
    });
    
    //~ reload_doc_structure();
});
