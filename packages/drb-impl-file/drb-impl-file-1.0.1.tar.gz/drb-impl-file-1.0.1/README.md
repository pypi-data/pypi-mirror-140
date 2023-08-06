# FileNode Implementation
This drb-impl-file module implements file protocol access with DRB data model. It is able to navigates among the file systems.

## File Factory and File Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.impl`.<br/>
The implementation name is `file`.<br/>
The factory class is encoded into `drb_impl_file.drb_impl_file`.<br/>

The file factory creates a FileNode from an existing path only, otherwise, a `DrbFileNodeFactoryException` exception is raised.

The FileNode can be instantiated from a single path or an uri. The `Path` class and its subclasses `ParsedPath` provided in drb core module can help to manage these inputs.

## limitations
The current version does not manage child modification and insertion.

## Using this module
To include this module into your project, the `drb-impl-file` module shall be referenced into `requirement.txt` file, or the following pip line can be run:

```commandline
pip install drb-impl-file
```
