import os
from skimage import io
from skimage.filters import laplace
import numpy as np
from typing import List, Tuple
import aicspylibczi
from nd2reader import ND2Reader
from icecream import ic

# ap = argparse.ArgumentParser(description="Extract tif from an image and count neurons and ganglia.")
# ap.add_argument('file_path',type=str,help="Path (relative or absolute) to target image")
# ap.add_argument('-o', '--out_dir', type=str, help="Root directory where output should be stored, default is base dir of the input image")
# ap.add_argument('-c', '--c_number', default=0, type=int, help="indexes (start at 0) of the channel contains the marker of interest. Default = 0.")


# ap.add_argument('-i', '--shape_indexes', default=None, type=int, help="index (start at 0) of the z-stack that needs to be extracted.")
# ap.add_argument('-t', '--tile_size', default=None, type=int, nargs=2, help="Tuple representing targetted tile size (X-Y). Example: `-t 2000 2000`. Default is no tiling behaviour")

# args = ap.parse_args()
# # if no out_dir is given, take the base dir of the input image
# if args.out_dir is None:
#     args.out_dir = os.path.dirname(args.file_path)

def getMostInFocusImage(image_array_list: List[np.array]) -> Tuple[np.array, int]:  
    """Gets most in focus image and its index from a list of image-arrays.

    Parameters
    ----------
    image_array_list : List[np.array]
        image_array_list

    Returns
    -------
    Tuple[np.array, int]

    """
    stdev_list = []
    for image in image_array_list:
        # calculate edges in image
        edged = laplace(image)
        # Calculate stdev of edges
        stdev = np.std(edged)
        stdev_list.append(stdev)
    # Find largest stdev in list
    largest = max(stdev_list)
    # Fidn which index it is to link back to the original list
    index = stdev_list.index(largest)
    return image_array_list[index], index

def readImage(file_path: str) -> Tuple[np.array, str]:
    """Reads in image-file and returns both the image and it's file type.

    Parameters
    ----------
    file_path : str
        file_path

    Returns
    -------
    Tuple[np.array, str]

    """
    if file_path.lower().endswith((".tif", ".tiff")):
        image = io.imread(file_path)
        img_type = "tif"
        img_shape = image.shape
        return image, img_type, img_shape
    if file_path.lower().endswith(".czi"):
        image = aicspylibczi.CziFile(file_path)
        img_type = "czi"
        img_shape  = image.get_dims_shape()[0]
        return image, img_type, img_shape
    if file_path.lower().endswith(".nd2"):
        with ND2Reader(file_path) as image:
            img_type = "nd2"
            img_shape = image.sizes
            return file_path, img_type, img_shape


def extractMostInFocusZstack(image: np.ndarray, z_shape_index:int = -1) -> np.ndarray:
    """Extract the most in focus z-stack of an image.

    Parameters
    ----------
    image : np.ndarray
        image
    z_shape_index : int
        index that indicates which position in the image.shape contains the z-axis.

    Returns
    -------
    np.ndarray

    """
    if not len(image.shape) > 2:
        raise ValueError(f"Image shape expected to be larger than 2, image shape is {image.shape}")
    img_list = []
    for i in range(image.shape[z_shape_index]):
        img_list.append(np.take(image, i, z_shape_index))
    mostInFocusImage = getMostInFocusImage(img_list)
    return mostInFocusImage



def extractSingleImages(image: str or np.ndarray, indexes_dict: dict, image_type: str, filename: str):
    """Extract from multi-dimensional input images all singe-stack images indicated by the indexes dict.

    Parameters
    ----------
    image : np.ndarray
        multi-dimensional input image
    indexes_dict : dict
        dict where keys are the shape-indexes and their values are indexes of which channels in that axis to extract. The combination of all key-value pairs will be extracted into single-channel images
    image_type : str
        image_type
    filename : str
        filename
    """
    if image_type == "tif":
        for shape_index, channel_indexes in indexes_dict.items():
            if isinstance(channel_indexes, int): # if it's only one channel, it'ss give an iterable error, so we gotta make it a list
                channel_indexes = [channel_indexes] 
            for channel_index in channel_indexes:
                if shape_index == None:
                    extracted_image = np.take(image, channel_index, axis=-1)
                else:
                    extracted_image = np.take(image, channel_index, axis=shape_index)
                io.imsave(f"{os.path.splitext(filename)[0]}_i{shape_index}_c{channel_index}.tif", extracted_image)
            
    elif image_type == "czi":
        for shape_index, channel_indexes in indexes_dict.items():
            # now we assume the shape indexes are letters referring to czi stuff
            if isinstance(channel_indexes, int): # if it's only one channel, it'ss give an iterable error, so we gotta make it a list
                channel_indexes = [channel_indexes] 
            for channel_index in channel_indexes:
                extracted_image,shape = image.read_image(shape_index=channel_index)
                extracted_image = extracted_image[0,0,0,0,0,:,:]
                io.imsave(f"{os.path.splitext(filename)[0]}_i{shape_index}_c{channel_index}.tif", extracted_image )
    elif image_type == "nd2":
        with ND2Reader(image) as images:
            for shape_index, channel_indexes in indexes_dict.items():
                if isinstance(channel_indexes, int): # if it's only one channel, it'ss give an iterable error, so we gotta make it a list
                    channel_indexes = [channel_indexes] 
                for channel_index in channel_indexes:
                    extracted_image = images.get_frame_2D(c=channel_index)
                    io.imsave(f"{os.path.splitext(filename)[0]}_i{shape_index}_c{channel_index}.tif", extracted_image)


if __name__ == '__main__':
    # image, img_type, img_shape = readImage("/home/david/Documents/enteric_neuron_tools/data/Slide2-1-2_Channel647,555,488_Seq0008.nd2")
    # test_dict = {'c':[0,1,2]}
    # extractSingleImages(image, test_dict, img_type, filename="/home/david/Documents/enteric_neuron_tools/data/Slide2-1-2_Channel647,555,488_Seq0008.nd2")

    with ND2Reader(image) as image:
        test_img = image.get_frame_2D(c=0, t=0)
