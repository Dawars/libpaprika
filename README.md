# LibPaprika
<p align="center">
 <img src="./images/banner.jpg" width="400"/>
</p>

## Introduction

_LibPaprika_ is a Python library that makes it easy to render 3D meshes on servers very efficiently.

Here is an example render:
 <img src="./images/hand_manifold.png" width="400"/>


## Example Usage

```python3
import libpaprika

renderer = libpaprika.ModelRenderer(num_vertices=778, faces=face_indices)

image = renderer.render(vertices, color=(1, 0, 0), background=(0.9, 0.9, 0.9))

```