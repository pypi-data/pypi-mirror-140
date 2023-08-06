import os

import streamlit as st
import streamlit.components.v1 as components

import pathlib
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("autograde_visualizer"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "autograde_visualizer",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("autograde_visualizer", path=build_dir)


@st.cache(allow_output_mutation=True)
def get_bucket():
    cred = credentials.Certificate('autograde_firebase.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'autograde-demo.appspot.com'
    })
    bucket = storage.bucket()
    return bucket

@st.cache()
def get_data(short_id):
    bucket = get_bucket()
    for blob in bucket.list_blobs():
        p = pathlib.Path(blob.name)
        if p.suffix == '.json':
            if 'shortId' in blob.metadata and blob.metadata['shortId'] == short_id:
                json_contents = blob.download_as_text()
                return json.loads(json_contents)
    return None


@st.cache()
def get_audio_file(filename):
    bucket = get_bucket()
    for blob in bucket.list_blobs():
        p = pathlib.Path(blob.name)
        if p.name == filename:
            blob.download_to_filename(filename)
            return filename

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def draw_alignment(json_data, audioFilename, key=None):
    """Create a new instance of "autograde_visualizer".

    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    #component_value = 
    _component_func(json=json_data, audioFilename=audioFilename, key=key, default=0)
    
    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    #return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run autograde_visualizer/__init__.py`
if not _RELEASE:
    st.subheader("Download Autograde data")

    short_id = st.text_input("Enter a short id", value="")
    if short_id:
        j = get_data(short_id)
        filename = get_audio_file(j['audioFilename'])
        draw_alignment(j, filename, key="foo")
        st.audio(filename)

