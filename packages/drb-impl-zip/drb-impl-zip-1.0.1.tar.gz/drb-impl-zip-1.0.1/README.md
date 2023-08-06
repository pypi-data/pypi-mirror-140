# ZipNode Implementation
This drb-impl-zip module implements access to zip containers with DRB data model. It is able to navigates among the zip contents.
## Zip Factory and Zip Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.impl`.<br/>
The implementation name is `zip`.<br/>
The factory class is encoded into `drb_impl_zip.file_zip_node`.<br/>

The zip factory creates a ZipNode from an existing zip content. It uses a base node to access the content data using a streamed implementation from the base node.

The base node can be a DrbFileNode, DrbHttpNode, DrbTarNode or any other nodes able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) zip content.
## limitations
The current version does not manage child modification and insertion. ZipNode is currently read only.
## Using this module
To include this module into your project, the `drb-impl-zip` module shall be referenced into `requirements.txt` file, or the following pip line can be run:
```commandline
pip install drb-impl-zip
```
