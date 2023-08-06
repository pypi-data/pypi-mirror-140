import os
from typing import Dict

import streamlit.components.v1 as components
import streamlit as st

# Toggle this to True when creating a release
_RELEASE = True

if _RELEASE:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend/build")

    _st_vtkjs = components.declare_component("streamlit_vtkjs", path=build_dir)
else:
    _st_vtkjs = components.declare_component(
        "streamlit_vtkjs", url="http://localhost:3001"
    )

def st_vtkjs(
    key: str, *, 
    content: bytes = None, 
    toolbar: bool = True, 
    sidebar: bool = True,
    subscribe: bool = True,
    clear: bool = True, 
    style: Dict = None
):
    """Streamlit VTKJS component.

    Args:
        key: A unique string for this instance of the viewer.
        content: A VTKJS file content.
        toolbar: A boolean to show or hide the toolbar in the viewer. Default is set to True.
        sidebar: A boolean to show or hide the sidebar in the viewer. Default is set to True.
        subscribe: A boolean to subscribe or unsubscribe the VTKJS file content. Default is set to True.
        clear: A boolen to clear the current contents from the viewer when loading the
            new content. Default is set to True.
        style: A dictionary to set the style for the viewer. The key and values can be
            any CSS style attribute. Default {"border": "1px solid #d0d7de", "borderRadius": "2px"}

    """

    style = style or {"border": "1px solid #d0d7de", "borderRadius": "2px"}
    return _st_vtkjs(file=content, toolbar=toolbar, sider=sidebar, subscribe=subscribe, clear=clear, style=style, key=key)

if not _RELEASE:
    st.set_page_config(page_title="Test VTKJS in Streamlit", layout="wide")

    st.title("VTKJS in Streamlit!")
    
    toolbar = st.checkbox('Toolbar', value=True, key='toolbar_toggle', help='Show/Hide the toolbar.')
    sidebar = st.checkbox('Sidebar', value=True, key='sidebar_toggle', help='Show/Hide the side toolbar.')
    subscribe = st.checkbox('Subscribe', value=False, key='subscribe_toggle', help='Toggles whether the viewer will return its state to Streamlit or not.')
    clear = st.checkbox('Clear', value=True, key='clear_toggle', help='Toggles clearing the viewer when loading a new model.')

    _file = st.file_uploader(
        label=".vtkjs scene uploader",
        type=["vtkjs", "vtk", "vtp"],
        help="Upload a .vtkjs scene file"
    )

    content = _file.getvalue() if _file else None

    viewer_state = st_vtkjs(
              "foobar",
              content=content,
              toolbar=st.session_state.toolbar_toggle,
              sidebar=st.session_state.sidebar_toggle,
              subscribe=st.session_state.subscribe_toggle,
              clear=st.session_state.clear_toggle,
              style={
                  "height": "400px",
              },
            )
    
    if st.session_state.subscribe_toggle :
      st.json(viewer_state)
