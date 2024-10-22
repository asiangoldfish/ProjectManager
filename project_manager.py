import gi
import os
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

class ProjectManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Project Manager")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Connect the key-press-event to the window
        self.connect("key-press-event", self.on_key_press)

        # Determine config file path
        xdg_config_home = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        proman_config_dir = os.path.join(xdg_config_home, 'proman')

        # Ensure the directory exists
        os.makedirs(proman_config_dir, exist_ok=True)

        # Path to the projects file
        self.config_file = os.path.join(proman_config_dir, 'projects.txt')
        self.projects = self.load_projects()

        # Set up the layout
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        # Project list
        self.project_list = Gtk.ListBox()
        self.update_project_list()
        self.vbox.pack_start(self.project_list, True, True, 0)

        # Button to remove a project
        self.remove_button = Gtk.Button(label="Remove Project")
        self.remove_button.set_sensitive(False)
        self.remove_button.connect("clicked", self.on_remove_project)
        self.vbox.pack_start(self.remove_button, False, False, 0)

        # Button to open project in VSCode
        self.open_vscode_button = Gtk.Button(label="Open in VSCode")
        self.open_vscode_button.set_sensitive(False)
        self.open_vscode_button.connect("clicked", self.on_open_vscode)
        self.vbox.pack_start(self.open_vscode_button, False, False, 0)

        # Button to open Alacritty terminal
        self.open_terminal_button = Gtk.Button(label="Open Terminal")
        self.open_terminal_button.set_sensitive(False)
        self.open_terminal_button.connect("clicked", self.on_open_terminal)
        self.vbox.pack_start(self.open_terminal_button, False, False, 0)

        # Button to add a project
        self.add_button = Gtk.Button(label="Add Project")
        self.add_button.connect("clicked", self.on_add_project)
        self.vbox.pack_start(self.add_button, False, False, 0)

        # Button to close the application
        self.close_button = Gtk.Button(label="Close")
        self.close_button.connect("clicked", self.on_close_button_clicked)
        self.vbox.pack_start(self.close_button, False, False, 0)

        # Connect selection change signal
        self.project_list.connect("row-selected", self.on_project_selected)

    def load_projects(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []

    def update_project_list(self):
        self.project_list.foreach(lambda row: self.project_list.remove(row))  # Clear existing rows
        for project in self.projects:
            self.project_list.add(Gtk.ListBoxRow(child=Gtk.Label(project)))
        self.project_list.show_all()

    def on_project_selected(self, list_box, row):
        self.remove_button.set_sensitive(row is not None)
        self.open_vscode_button.set_sensitive(row is not None)
        self.open_terminal_button.set_sensitive(row is not None)

    def on_remove_project(self, button):
        selected_row = self.project_list.get_selected_row()
        if selected_row:
            project = selected_row.get_child().get_text()
            self.projects.remove(project)
            self.save_projects()
            self.update_project_list()

    def on_open_vscode(self, button):
        selected_row = self.project_list.get_selected_row()
        if selected_row:
            project_path = selected_row.get_child().get_text()
            # Open the project in VSCode
            subprocess.Popen(["code", project_path])

            Gtk.main_quit()

    def on_open_terminal(self, button):
        selected_row = self.project_list.get_selected_row()
        if selected_row:
            project_path = selected_row.get_child().get_text()
            # Open the Alacritty terminal in the project's directory
            subprocess.Popen(["alacritty", "--working-directory", project_path])

            Gtk.main_quit()

    def on_add_project(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select a Project Directory", 
            parent=self, 
            action=Gtk.FileChooserAction.SELECT_FOLDER,  # Change this to select folders
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )


        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            project_path = dialog.get_filename()  # Get the selected file path
            if project_path and project_path not in self.projects:  # Check if the path is valid and not already in the list
                self.projects.append(project_path)
                self.save_projects()
                self.update_project_list()
        dialog.destroy()

    def save_projects(self):
        try:
            with open(self.config_file, 'w') as f:
                f.writelines(f"{project}\n" for project in self.projects)
        except Exception as e:
            print(f"Error saving projects: {e}")

    def on_close_button_clicked(self, button):
        Gtk.main_quit()  # This will close the application


    def on_key_press(self, widget, event):
        # Check if the Escape key is pressed
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()  # This will close the application


if __name__ == "__main__":
    app = ProjectManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
