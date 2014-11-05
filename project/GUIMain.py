# -*- coding: utf-8 -*-

import pygtk
import sys
import gtk
import gtk.glade
import os
import mimetypes
from ImageProcessor import ImageProcessor
pygtk.require("2.0")

__author__ = 'emontenegro'


class GUIMain:
    # constants
    GLADE_FILE = "./NovappGui/GUI_Interface.glade"
    MAIN_WINDOW = "mainwindow"
    TREE_VIEW = "treeview"
    IMAGE_DISPLAY = "imagedisplayer"
    LABEL_DIRECTORY = "labeldirectory"
    WINDOW_STAGES = "windowstages"

    IMG_MID_GRAPH = "imagemidgraph"
    IMG_TOP_GRAPH = "imagetopgraph"
    IMG_BOT_GRAPH = "imagebotgraph"

    # attributes
    glade = None
    mainWindow = None
    dialog = None
    tree_view = None
    window_stages = None
    image_display = None

    image_bot_graph = None
    image_mid_graph = None
    image_top_graph = None

    display_label = None
    current_image_path = None

    current_page = 0
    image_processor = None



    # local path
    currentPath = os.getcwd()

    def __init__(self):
        self.glade = gtk.Builder()
        self.glade.add_from_file(self.GLADE_FILE)

        # connecting signals
        dic = {
            "on_firstwindow_destroy": self.quit,
            "on_firstwindow_delete_event": self.quit,
            "on_buttonnext_clicked": self.button_next,
            "on_buttonback_clicked": self.button_back,
            "on_buttonclose_clicked": self.quit,
            "on_buttonselectdirectory_clicked": self.open_search_dialog,
            "on_treeview_cursor_changed": self.element_selected,
        }
        self.glade.connect_signals(dic)

        # initializing components
        self.mainWindow = self.glade.get_object(self.MAIN_WINDOW)
        self.tree_view = self.glade.get_object(self.TREE_VIEW)
        self.initialize_tree_view()
        self.window_stages = self.glade.get_object(self.WINDOW_STAGES)
        self.image_display = self.glade.get_object(self.IMAGE_DISPLAY)
        self.display_label = self.glade.get_object(self.LABEL_DIRECTORY)

        self.image_bot_graph = self.glade.get_object(self.IMG_BOT_GRAPH)
        self.image_mid_graph = self.glade.get_object(self.IMG_MID_GRAPH)
        self.image_top_graph = self.glade.get_object(self.IMG_TOP_GRAPH)

        GUIMain.set_text_directory(self.display_label, self.currentPath)
        
        self.mainWindow.show_all()

    def initialize_tree_view(self):
        store = self.populate_store(self.currentPath)
        self.tree_view.set_model(store)
        renderer_1 = gtk.CellRendererText()
        column_1 = gtk.TreeViewColumn('File Name', renderer_1, text=0)
        column_1.set_sort_column_id(0)
        self.tree_view.append_column(column_1)
        renderer_2 = gtk.CellRendererText()#(xalign=1)
        column_2 = gtk.TreeViewColumn('Size in bytes', renderer_2, text=1)
        column_2.set_sort_column_id(2)
        self.tree_view.append_column(column_2)
        # scrollwindow = builder.get_object("scrolledwindow")
        # scrollwindow.set_policy(gtk.PolicyType.NEVER, gtk.PolicyType.AUTOMATIC)

    def element_selected(self, menuitem, data=None):
        model, treeiter = menuitem.get_selection().get_selected()
        if treeiter is not None and model[treeiter][0].endswith(".png"):
            self.image_display.clear()
            self.current_image_path = self.currentPath+"/"+model[treeiter][0]
            self.image_display.set_from_file(self.current_image_path)
        else:
            dialog = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, "Archivo seleccionado incorrecto")
            dialog.format_secondary_text("Por el momento, solo funciona con archivos .PNG")
            dialog.run()
            dialog.destroy()

    def open_search_dialog(self, menuitem, data=None):
        dialog = gtk.FileChooserDialog(title="Open Folder ...", parent=None, action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        dialog.set_select_multiple(False)

        dialog.set_current_folder_uri(self.currentPath)
        response = dialog.run()

        if response == gtk.RESPONSE_ACCEPT:
            directory = dialog.get_filenames()[0]
            self.tree_view.set_model(self.populate_store(directory))
            self.currentPath = directory
        else:
            directory = None

        dialog.destroy()
        self.set_text_directory(self.display_label, directory)

    def button_next(self, menuitem, data=None):
        self.window_stages.next_page()
        self.current_page = self.window_stages.get_current_page()
        if self.current_page == 2:
            if self.current_image_path is not None and len(self.current_image_path) > 0:
                self.process_image()
            else:
                self.current_page = self.window_stages.get_current_page()-1
                self.window_stages.set_current_page(self.current_page)
                dialog = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, "Archivo no seleccionado")
                dialog.format_secondary_text("Para pasar a esta etapa, debe tener un archivo válido seleccionado")
                dialog.run()
                dialog.destroy()


    def button_back(self, menuitem, data=None):
        self.window_stages.prev_page()
        self.current_page = self.window_stages.get_current_page()

    def quit(self, menuitem, data=None):
        dialog = gtk.MessageDialog(self.mainWindow, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, "Cerrar la aplicación")
        dialog.format_secondary_text("Está seguro que desea cerrar la aplicación?")
        response = dialog.run()
        if gtk.RESPONSE_YES == response:
            dialog.destroy()
            sys.exit(0)
        else:
            dialog.destroy()

    def process_image(self):
        self.image_processor = ImageProcessor(self.current_image_path)
        top_pattern, mid_pattern, bot_pattern = self.image_processor.start_processing()

        width, height = self.mainWindow.get_size()
        self.set_scaled_image(self.image_bot_graph, bot_pattern, width, height)
        self.set_scaled_image(self.image_mid_graph, mid_pattern, width, height)
        self.set_scaled_image(self.image_top_graph, top_pattern, width, height)

    @staticmethod
    def set_scaled_image(component, url, width, height):
        pixbuf = gtk.gdk.pixbuf_new_from_file(url)
        pixbuf = pixbuf.scale_simple(width/3, height/3, gtk.gdk.INTERP_BILINEAR)
        component.set_from_pixbuf(pixbuf)

    @staticmethod
    def populate_store(directory):
        store = gtk.ListStore(str, str, long)
        for filename in os.listdir(directory):
            if mimetypes.guess_type(filename)[0] is not None and "image" in mimetypes.guess_type(filename)[0]:
                size = os.path.getsize(os.path.join(directory, filename))
                store.append([filename, '{0:,}'.format(size), size])
        return store

    @staticmethod
    def set_text_directory(element, string):
        element.set_text("Path: {0}".format(string))

if __name__ == "__main__":
    try:
        a = GUIMain()
        gtk.main()
    except KeyboardInterrupt:
        pass