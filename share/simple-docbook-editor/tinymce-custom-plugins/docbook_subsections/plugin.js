/**
 * plugin.js
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

/*global tinymce:true */

tinymce.PluginManager.add('docbook_subsections', function(editor)
{
    function createSubsection()
    {
        var current_section_type = edited_section_node.attr("data-docbook-type");
        var new_section_type;
        if (current_section_type == "chapter")
        {
            new_section_type = "sect1";
        }
        else
        {
            new_section_type = "sect" + (parseInt(current_section_type.substring(4)) + 1);
        }
        editor.selection.setContent(editor.dom.createHTML("div", {class: "subsection " + new_section_type + " mceNonEditable", "data-docbook-type": new_section_type}, "<h1>New section</h1>") + editor.dom.createHTML("p", {}, "&nbsp;"));
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
