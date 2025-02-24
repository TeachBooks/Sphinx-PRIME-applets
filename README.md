# PRIME applets

```{admonition} User types
:class: tip
This section is useful for user type 3-5.
```
+++
{bdg-primary}`Sphinx Extension`

## Introduction

This extension provides an interface to include [PRIME applets](https://openla.ewi.tudelft.nl/) with relative ease.

## Applet directive

````md
```{applet}
:url: lines_and_planes/normal_equation_plane_origin
:fig: Images/image_shown_in_print_version.svg
:name: name_that_is_used_to_refer_to_this_figure
:class: dark-light
:title: This title is shown when you full-screen the applet

A plane through the point $P$.
```
````

::::{note}
The `url` parameter should be the part of the URL after `/applet/`. So if the full URL is `https://openla.ewi.tudelft.nl/applet/lines_and_planes/normal_equation_plane_origin`, you should set the parameter to `lines_and_planes/normal_equation_plane_origin`.
::::

## Parameters for an applet

Some parameters can be set for an applet. Only the `url`, `fig` and `name` parameters are required; the rest is optional. It is recommended to add a `status` to the applet, which can be `unreviewed`, `in-review` or `reviewed`.

````md
```{applet}
:url: lines_and_planes/normal_equation_plane_origin # Required url
:fig: Images/lines_and_planes/normal_equation_plane_origin.svg  # Image shown in print version
:status: reviewed # default is "unreviewed". Other options are "in-review" and "reviewed"
:name: Fig:InnerProduct:ProjectionVectorLine

A title that describes the applet
```
````

### Optional parameters

| Parameter                                                                                                                           | Description                                                                                  | Default      |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------ |
| `title`                                                                                                                             | A string that will be shown as the title of the applet when the applet is in fullscreen mode | ""           |
| `status`                                                                                                                            | The status of the applet. Can be `unreviewed`, `in-review` or `reviewed`                     | `unreviewed` |
| `width`                                                                                                                             | The width of the applet in pixels                                                            | 100%         |
| `height`                                                                                                                            | The height of the applet in pixels                                                           | 400px        |

### Control parameters

::::{warning}
Work in progress
::::

### 2D Specific parameters

::::{tip}
You should add split-\* before the parameter to make it apply to the right scene
::::

| Parameter  | Description                                  | Default |
| ---------- | -------------------------------------------- | ------- |
| position2D | The position of the applet in the 2D plane   | 0,0     |
| zoom2D     | The zoom level of the applet in the 2D plane | 1       |

### 3D Specific parameters

::::{tip}
You should add split-\* before the parameter to make it apply to the right scene
::::

| Parameter  | Description                                  | Default |
| ---------- | -------------------------------------------- | ------- |
| position3D | The position of the applet in the 3D plane   | 0,0,0   |
| zoom3D     | The zoom level of the applet in the 3D plane | 1       |

## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/Sphinx-PRIME-applets). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/Sphinx-PRIME-applets).

The `README.md` of the branch `manual` is also part of the [TeachBooks manual](https://teachbooks.io/manual/intro.html) as a submodule.