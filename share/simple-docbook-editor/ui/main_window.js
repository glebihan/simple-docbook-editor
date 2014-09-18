/**
 * main_window.js
 *
 * Copyright © 2014 Gwendal Le Bihan
 * 
 * This file is part of simple-docbook-editor.
 * 
 * Simple DocBook Editor is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Simple DocBook Editor is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Simple DocBook Editor.  If not, see <http://www.gnu.org/licenses/>.
 */

var doc_structure_closed_nodes = new Array();
var selected_doc_section = null;
var edited_section_id = 0;
var edited_section_node = null;
var saveTimeout = null;
var sourceSaveTimeout = null;
var current_file_browser_window = null;
var source_editor = null;
var parsing_error = null;
var app_config = {};
var first_config_load = true;
var translations = {};

function _(mesg)
{
    if (!translations[mesg])
    {
        alert("translate:" + mesg);
    }
    console.log(mesg + ":" + translations[mesg]);
    return (translations[mesg] ? translations[mesg] : mesg);
}

function set_translation(data)
{
    translations[data.mesg] = data.translation;
}

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
        jQuery("#maintabs").tabs("enable", 0);
        edited_section_node = jQuery(edit_data.html);
        tinymce.get("tinymcecontainer").setContent(edited_section_node.html());
    }
    else
    {
        if (jQuery("#maintabs").tabs("option", "active") != 1)
        {
            jQuery("#maintabs").tabs("option", "active", 1);
        }
        jQuery("#maintabs").tabs("disable", 0);
    }
    if (edited_section_id != edit_data.section_id && edit_data.edit_mode == "html")
    {
        tinymce.get("tinymcecontainer").undoManager.clear();
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

function set_parsing_error(error)
{
    parsing_error = error;
}

function show_alert(mesg)
{
    var dialog = jQuery("<div/>");
    dialog.html(mesg);
    var buttons = {};
    buttons[_("OK")] = function()
    {
        jQuery(this).dialog("close");
    };
    jQuery(dialog).dialog({
        title: _("Error"),
        buttons: buttons,
        modal: true
    });
}

function set_config(config)
{
    app_config = config;
    if (first_config_load)
    {
        first_config_load = false;
        
        jQuery('#doc_structure').tree(
        {
            data: [],
            autoOpen: true,
            dragAndDrop: false,
            onCanSelectNode: function(node)
            {
                if (parsing_error && node.id != edited_section_id)
                {
                    show_alert(parsing_error);
                    return false;
                }
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
                        if (parsing_error)
                        {
                            show_alert(parsing_error);
                        }
                        else
                        {
                            selected_doc_section = parseInt(jQuery(e.target).attr("data-section-id"));
                            load_doc_section(parseInt(jQuery(e.target).attr("data-section-id")));
                            reload_doc_structure();
                        }
                    }
                });
                editor.on('change', function(e)
                {
                    if (jQuery("#maintabs").tabs("option", "active") == 0)
                    {
                        save_editor_contents();
                    }
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
            toolbar: "bold italic underline strikethrough | cut copy paste | bullist numlist | undo redo | removeformat subscript superscript | image | add_docbook_subsection | code",
            relative_urls: false,
            content_style: (
                'div.subsection {background-color: #B3B3B3; cursor: pointer; padding: 5px; margin-bottom: 10px;}'
            ),
            object_resizing: "img,table,sup.footnote",
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
            indentUnit: 4,
            lineWrapping: app_config["Source Editor"].linewrapping
        });
        source_editor.on("change", function(editor, event)
        {
            if (jQuery("#maintabs").tabs("option", "active") == 1)
            {
                save_source_editor_contents();
            }
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
    }
}

jQuery(document).ready(function()
{
    alert("load_config");
});
