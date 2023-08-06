# DeepCAD-RT: Deep self-supervised learning for calcium imaging denoising

<img src="images/logo.PNG" width="600" align="middle">

### [Project page](https://cabooster.github.io/DeepCAD-RT/) | [Paper](https://www.nature.com/articles/s41592-021-01225-0)

## Contents

- [Overview](#overview)
- [Directory structure](#directory-structure)
- [Pytorch code](#pytorch-code)
- [Matlab GUI](#matlab-gui)
- [Results](#results)
- [License](./LICENSE)
- [Citation](#citation)

## Overview

Calcium imaging is inherently susceptible to detection noise especially when imaging with high frame rate or under low excitation dosage. However, calcium transients are highly dynamic, non-repetitive activities and a firing pattern cannot be captured twice. Clean images for supervised training of deep neural networks are not accessible. Here, we present DeepCAD, a **deep** self-supervised learning-based method for **ca**lcium imaging **d**enoising. Using our method, detection noise can be effectively removed and the accuracy of neuron extraction and spike inference can be highly improved.

DeepCAD is based on the insight that a deep learning network for image denoising can achieve satisfactory convergence even the target image used for training is another corrupted sampling of the same scene [[paper link]](https://arxiv.org/abs/1803.04189). We explored the temporal redundancy of calcium imaging and found that any two consecutive frames can be regarded as two independent samplings of the same underlying firing pattern. A single low-SNR stack is sufficient to be a complete training set for DeepCAD. Furthermore, to boost its performance on 3D temporal stacks, the input and output data are designed to be 3D volumes rather than 2D frames to fully incorporate the abundant information along time axis.

For more details, please see the companion paper where the method first appeared: 
["*Reinforcing neuron extraction and spike inference in calcium imaging using deep self-supervised denoising, Nature Methods (2021)*"](https://www.nature.com/articles/s41592-021-01225-0).



<img src="images/schematic.png" width="800" align="middle">



## Directory structure

```
DeepCAD-RT
|---DeepCAD_RT_pytorch #Pytorch implementation of DeepCAD-RT#
|---|---demo_train_pipeline.py
|---|---demo_test_pipeline.py
|---|---transfer_pth_to_onnx.py
|---|---deepcad
|---|---|---__init__.py
|---|---|---utils.py
|---|---|---network.py
|---|---|---model_3DUnet.py
|---|---|---data_process.py
|---|---|---buildingblocks.py
|---|---|---test_collection.py
|---|---|---train_collection.py
|---|---|---movie_display.py
|---|---notebooks
|---|---|---demo_train_pipeline.ipynb
|---|---|---demo_test_pipeline.ipynb
|---|---|---DeepCAD_RT_demo_colab.ipynb
|---|---datasets
|---|---|---DataForPytorch # project_name #
|---|---|---|---data.tif
|---|---pth
|---|---|---ModelForPytorch
|---|---|---|---model.pth
|---|---|---|---model.yaml
|---|---results
|---|---|--- # test results#
|---DeepCAD_RT_HA #Matlab GUI of DeepCAD-RT#
```

## Pytorch code

### Our environment 

* Ubuntu 16.04 
* Python 3.6
* Pytorch 1.8.0
* NVIDIA GPU (GeForce RTX 3090) + CUDA (11.1)

### Environment configuration

* Create a virtual environment, install Pytorch and DeepCAD package. In the 3rd step, please select the correct Pytorch version that matches your CUDA version from https://pytorch.org/get-started/previous-versions/.

```
$ conda create -n deepcadrt python=3.6
$ conda activate deepcadrt
$ pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
$ pip install deepcad
```

### Download the source code

```
$ git clone git://github.com/cabooster/DeepCAD-RT
$ cd DeepCAD-RT/DeepCAD_RT_pytorch/
```

### Demos

- Python file: 

  To try out the python file, please activate deepcadrt conda environment:

  ```
  $ conda activate deepcadrt
  $ cd DeepCAD-RT/DeepCAD_RT_pytorch/
  ```

  To  train your own DeepCAD-RT network, we recommend to start with the demo file `demo_train_pipeline.py`  in `DeepCAD_RT_pytorch` subfolder. You can try our demo files directly or edit some parameter appropriate to your hardware or data.

  **Example training**

  ```
  python demo_train_pipeline.py
  ```

  **Example test**

  ```
  python demo_test_pipeline.py
  ```

- Jupyter notebooks: 

  The notebooks provide a simple and friendly way to get into DeepCAD-RT. They are located in the `DeepCAD_RT_pytorch/notebooks`. To launch  the Jupyter notebooks:

  ```
  $ conda activate deepcadrt
  $ cd DeepCAD-RT/DeepCAD_RT_pytorch/notebooks
  $ jupyter notebook
  ```

- Colab notebooks: 

  You can also run DeepCAD-RT in google colab with a GPU: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/STAR-811/DeepCAD-RT/blob/main/DeepCAD_RT_pytorch/notebooks/DeepCAD_RT_demo_colab.ipynb)

## Matlab GUI

To achieve real-time denoising during imaging process, DeepCAD-RT is implemented on GPU with Nvidia TensorRT and delicately-designed time sequence to further accelerate the inference speed and decrease memory cost. We developed a user-friendly Matlab GUI for DeepCAD-RT , which is easy to install and convenient to use (has been tested on a Windows desktop with Intel i9 CPU and 128G RAM).  **Tutorials** on installing and using the GUI has been moved to [**this page**](https://github.com/STAR-811/DeepCAD-RT/tree/master/DeepCAD_RT_GUI).  

<div style="align: center">

​              <img src="images/GUI.png" width="600" align="middle">   

## Results

**1. Universal denoising for calcium imaging in zebrafish.**

[![IMAGE ALT TEXT](images/sv3_video.png)]( https://www.youtube.com/embed/GN0IO7bGoGg "Video Title")

**2. Denoising performance of DeepCAD-RT of neutrophils in the mouse brain in vivo.** 

[![IMAGE ALT TEXT](images/sv8_video.png)]( https://www.youtube.com/embed/eyLPVRcEGHs "Video Title")

**3. Denoising performance of DeepCAD-RT on a recently developed genetically encoded ATP sensor.**

[![IMAGE ALT TEXT](images/sv10_video.png)](https://www.youtube.com/embed/u1ejSaVvWiY "Video Title")

More demo videos are demonstrated on [our website](https://cabooster.github.io/DeepCAD-RT/Gallery/).

## Citation

If you use this code please cite the companion paper where the original method appeared: 

Li, X., Zhang, G., Wu, J. et al. Reinforcing neuron extraction and spike inference in calcium imaging using deep self-supervised denoising. Nat Methods (2021). [https://doi.org/10.1038/s41592-021-01225-0](https://www.nature.com/articles/s41592-021-01225-0)

```
@article{li2021reinforcing,
  title={Reinforcing neuron extraction and spike inference in calcium imaging using deep self-supervised denoising},
  author={Li, Xinyang and Zhang, Guoxun and Wu, Jiamin and Zhang, Yuanlong and Zhao, Zhifeng and Lin, Xing and Qiao, Hui and Xie, Hao and Wang, Haoqian and Fang, Lu and others},
  journal={Nature Methods},
  pages={1--6},
  year={2021},
  publisher={Nature Publishing Group}
}
```



