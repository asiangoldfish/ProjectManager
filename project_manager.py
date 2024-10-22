import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ProjectManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Project Manager")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Load projects from config file
        self.config_file = "projects.txt"
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

        # Connect selection change signal
        self.project_list.connect("row-selected", self.on_project_selected)

        # Button to add a project
        self.add_button = Gtk.Button(label="Add Project")
        self.add_button.connect("clicked", self.on_add_project)
        self.vbox.pack_start(self.add_button, False, False, 0)

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

    def on_remove_project(self, button):
        selected_row = self.project_list.get_selected_row()
        if selected_row:
            project = selected_row.get_child().get_text()
            self.projects.remove(project)
            self.save_projects()
            self.update_project_list()

    # def on_add_project(self, button):
    #     dialog = Gtk.FileChooserDialog("Select a Project", self, 
    #                                    Gtk.FileChooserAction.OPEN,
    #                                    ("Cancel", Gtk.ResponseType.CANCEL,
    #                                     "Open", Gtk.ResponseType.OK))

    #     response = dialog.run()
    #     if response == Gtk.ResponseType.OK:
    #         project_path = dialog.get_filename()
    #         if project_path not in self.projects:
    #             self.projects.append(project_path)
    #             self.save_projects()
    #             self.update_project_list()
    #     dialog.destroy()

    # def save_projects(self):
    #     with open(self.config_file, 'w') as f:
    #         f.writelines(f"{project}\n" for project in self.projects)

    def on_add_project(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select a Project", 
            parent=self, 
            action=Gtk.FileChooserAction.OPEN,
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



if __name__ == "__main__":
    app = ProjectManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
