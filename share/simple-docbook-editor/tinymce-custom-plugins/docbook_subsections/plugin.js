/**
 * plugin.js
 *
 * Copyright, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://www.tinymce.com/license
 * Contributing: http://www.tinymce.com/contributing
 */

/*global tinymce:true */

tinymce.PluginManager.add('docbook_subsections', function(editor)
{
    function createSubsection()
    {
        var current_section_type = jQuery(editor.getBody().firstChild).attr("data-docbook-type");
        var new_section_type;
        if (current_section_type == "chapter")
        {
            new_section_type = "sect1";
        }
        else
        {
            new_section_type = "sect" + (parseInt(current_section_type.substring(4)) + 1);
        }
        editor.selection.setContent(editor.dom.createHTML("div", {class: "subsection " + new_section_type + " mceNonEditable", "data-docbook-type": new_section_type}, "<h1>New section</h1>"));
        do_save_editor_contents();
        reload_doc_structure();
        load_doc_section(edited_section_id);
	}
    
	editor.addButton('add_docbook_subsection',
    {
		icon: 'newdocument',
		tooltip: 'Insert subsection',
		onclick: createSubsection,
        stateSelector: null
	});

	editor.addMenuItem('add_docbook_subsection',
    {
		icon: 'sub',
		text: 'Insert subsection',
		onclick: createSubsection,
		context: 'insert',
		prependToContext: true
	});
});
