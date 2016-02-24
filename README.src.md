[:var_set('', """
# Compile command
aoikdyndocdsl -s README.src.md -n aoikdyndocdsl.ext.all::nto -g README.md
""")
]\
[:HDLR('heading', 'heading')]\
# AoikProjectSpecificPackages
A Sublime Text plugin to support project-specific package settings.

Tested working with:
- Sublime Text 2
- Sublime Text 3

![Image](/screencast.gif)

## Table of Contents
[:toc(beg='next', indent=-1)]

## Setup

### Setup via git
Clone this repository to Sublime Text's **Packages** directory (Preferences - Browse Packages...):
```
git clone https://github.com/AoiKuiyuyou/AoikProjectSpecificPackages-SublimeText AoikProjectSpecificPackages
```

Make sure the repository directory is renamed to **AoikProjectSpecificPackages**
(without the "-SublimeText" postfix), otherwise it may not work well.

## Usage
In your project directory (where the ".sublime-project" file resides), create
a directory named "sublime_packages". Put in your project-specific package
settings there, as you would usually do in Sublime Text's "Packages" directory.
Then when a view of the project gets focus, this plugin will copy files under
the "sublime_packages" directory to Sublime Text's "Packages" directory, and
Sublime Text will reload the settings on-the-fly.

**CAUTION**: Existing files under Sublime Text's "Packages" directory will be
overwritten. Back up your settings there before starting using this plugin.

The copying will be triggered when opening a project, or switching from one
project's view to another project's view. It will not be triggered when
switching between views of the same project. So there is no worry of
unnecessary copying.

An alternative directory name or path instead of the default "sublime_packages"
can be specified in the ".sublime-project" file's "settings" dictionary, e.g.:
```
{
    "settings":
    {
        "project_specific_packages_directory": "sublime_text_packages"
    }
}

```

There is a gotcha for Sublime Text 2. Because API "Window.project_file_name" is
not available in Sublime Text 2, a heuristic method is used to find the
project file. This requires that in Sublime Text 2 you should keep the
".sublime-project" file open in a view. The first ".sublime-project" file found
open will be used as the project file.
