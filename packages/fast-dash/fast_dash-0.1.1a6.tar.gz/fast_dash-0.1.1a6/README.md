# Overview


<p align="center">
<a href="https://pypi.python.org/pypi/fast_dash">
    <img src="https://img.shields.io/pypi/v/fast_dash.svg"
        alt = "Release Status">
</a>

<a href="https://github.com/dkedar7/fast_dash/actions">
    <img src="https://github.com/dkedar7/fast_dash/actions/workflows/release.yml/badge.svg" alt="CI Status">
</a>


<a href="https://github.com/dkedar7/fast_dash/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/dkedar7/fast_dash" alt="MIT License">
</a>

<a href="https://dkedar7.github.io/fast_dash/">
    <img src="https://img.shields.io/badge/Docs-MkDocs-<COLOR>.svg" alt="Documentation">
</a>

</p>


<p align="center">
  <a href="https://dkedar7.github.io/fast_dash/"><img src="https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/logo.png" alt="Fast Dash logo"></a>
</p>
<p align="center">
    <em>Open source, Python-based tool to develop web applications lightining fast.</em>
</p>


---


* Documentation: <https://dkedar7.github.io/fast_dash/>
* Source code: <https://github.com/dkedar7/fast_dash/>

---

Fast Dash is a Python module that makes the development of web applications fast and easy. It is built on top of Plotly Dash and can be used to build web interfaces for Machine Learning models or to showcase any proof of concept withoout the hassle of developing UI from scratch.

## Simple example

Run your app with three simple steps:

```python
from fast_dash.App import App
from fast_dash.Components import TextInput, TextOutput

# Step 1: Define your callback function
def callback_function(input_text):
    # Code to process text
    processed_text = input_text
    return processed_text

# Step 2: Specify the input/ output widgets
app = App(callback_fn=callback_fn, 
        inputs=[TextInput()], 
        outputs=[TextOutput()], 
        title='My App')

# Step 3: Run your app!
app.run()

# * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

Output:

![Simple example](https://raw.githubusercontent.com/dkedar7/fast_dash/main/docs/assets/simple_example.gif)

## Features

- No need to build UI from scratch
- Launch an app only by specifying the types of inputs and outputs
- Flask-based backend allows easy scalability and widespread compatibility
- Option to customize per one's interest

Some features are coming up in future releases:

- More input and output components
- Deploy to Heroku
- and many more.

## Community

Fast Dash is built on open-source. You are encouraged to share your own projects, which will be highlighted on a common community gallery that's upcoming. Join us on [Discord](https://discord.gg/B8nPVfPZ6a).

## Credits

Fast Dash is build on top of [Plotly Dash](https://github.com/plotly/dash) and the documentation is inspired from [FastAPI's docs](https://fastapi.tiangolo.com/) project template. It is inpired from [gradio](https://github.com/gradio-app/gradio).