
import io
import six
from soma import aims
import anatomist.direct.api as ana
from soma.qt_gui.qt_backend import Qt
from PIL import Image, ImageChops
from six.moves import zip

'''Useful functions and variable to take snapshot'''

VIEW_QUATERNIONS = {'left': [0.5, 0.5, 0.5, 0.5],
                    'right': [0.5, -0.5, -0.5, 0.5],
                    'back left': [-0.24415700000000001,
                                  -0.66425900000000004,
                                  -0.66440299999999997,
                                  -0.24024699999999999],
                    'back right': [0.23693700000000001,
                                   -0.66650600000000004,
                                   -0.66561400000000004,
                                   0.237873],
                    'left bottom': [-0.65499700000000005,
                                    -0.65245200000000003,
                                    -0.26732800000000001,
                                    -0.2717],
                    'right bottom': [0.653748,
                                     -0.65495999999999999,
                                     -0.26623000000000002,
                                     0.26974500000000001],
                    'front left': [-0.66398100000000004,
                                   -0.24052299999999999,
                                   -0.238736,
                                   -0.66654899999999995],
                    'front right': [-0.664493,
                                    0.23544699999999999,
                                    0.24188200000000001,
                                    -0.666717],
                    'front top left': [-0.42310900000000001,
                                       -0.17835200000000001,
                                       -0.33598600000000001,
                                       -0.82235800000000003],
                    'front top right': [-0.42310900000000001,
                                        0.17835200000000001,
                                        0.33598600000000001,
                                        -0.82235800000000003],
                    'left top': [-0.27245700359344499,
                                 -0.27196499705314597,
                                 -0.65204000473022505,
                                 -0.65318101644516002],
                    'right top': [-0.272103011608124,
                                  0.27079299092292802,
                                  0.65114599466323897,
                                  -0.65470701456069902],
                    'A': [1, 0, 0, 0],
                    'C': [0.70710700000000004, 0, 0, 0.70710700000000004],
                    'S': [0.5, 0.5, 0.5, 0.5]}

SLICE_QUATERNIONS = {'A': [0, 0, 0, 1],
                     'C': [0.70710700000000004, 0, 0, 0.70710700000000004],
                     'S': [-0.5, -0.5, -0.5, 0.5]}


def autocrop(img, bgcolor):
    ''' Crops an image given a background color '''

    if img.mode == "RGBA":
        img_mode = "RGBA"
    elif img.mode != "RGB":
        img_mode = "RGB"
        img = img.convert("RGB")
    else:
        img_mode = "RGB"
    bg = Image.new(img_mode, img.size, bgcolor)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    return img.crop(bbox)


def qt_to_pil_image(qimg):
    ''' Converting a Qt Image or Pixmap to PIL image '''

    buffer = Qt.QBuffer()
    buffer.open(Qt.QIODevice.ReadWrite)
    qimg.save(buffer, 'PNG')
    strio = io.BytesIO()
    strio.write(buffer.data().data())
    buffer.close()
    strio.seek(0)
    pil_im = Image.open(strio)
    return pil_im


def get_snapshot(w, size):
    ''' From a AWindow, returns a PIL screenshot '''
    # TODO : use function in snap
    # Converting to PIL image
    qimg = w.snapshotImage(size[0], size[1])
    pil_im = qt_to_pil_image(qimg)
    # Cropping
    cropped_im = autocrop(pil_im, (0, 0, 0))

    return cropped_im


def detect_min_max_slices(data, slice_directions=['A'], threshold=0):
    '''
    Returns first and last non empty slices
    slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
    '''

    d = data.arraydata()
    slices_minmax = {}
    for direction in slice_directions:
        if direction == 'A':
            n_slices = d.shape[1]
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices - 1
            s = d[0, first_nonempty_slice, :, :]
            while (s[s > threshold].size == 0 and first_nonempty_slice < n_slices-1):
                first_nonempty_slice += 1
                s = d[0, first_nonempty_slice, :, :]

            s = d[0, last_nonempty_slice, :, :]
            while (s[s > threshold].size == 0 and last_nonempty_slice > 0):
                last_nonempty_slice -= 1
                s = d[0, last_nonempty_slice, :, :]
        elif direction == 'C':
            n_slices = d.shape[2]
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices - 1
            s = d[0, :, first_nonempty_slice, :]
            while (s[s > threshold].size == 0 and first_nonempty_slice < n_slices-1):
                first_nonempty_slice += 1
                s = d[0, :, first_nonempty_slice, :]

            s = d[0, :, last_nonempty_slice, :]
            while (s[s > threshold].size == 0 and last_nonempty_slice > 0):
                last_nonempty_slice -= 1
                s = d[0, :, last_nonempty_slice, :]
        elif direction == 'S':
            n_slices = d.shape[3]
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices - 1
            s = d[0, :, :, first_nonempty_slice]
            while (s[s > threshold].size == 0 and first_nonempty_slice < n_slices-1):
                first_nonempty_slice += 1
                s = d[0, :, :, first_nonempty_slice]

            s = d[0, :, :, last_nonempty_slice]
            while (s[s > threshold].size == 0 and last_nonempty_slice > 0):
                last_nonempty_slice -= 1
                s = d[0, :, :, last_nonempty_slice]
        if first_nonempty_slice >= last_nonempty_slice:
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices - 1
        slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
    return slices_minmax


def get_slice_position(d, s, voxel_size=[1.0, 1.0, 1.0, 1.0]):
    if d == 'A':
        res = [0, 0, s * voxel_size[2], 0]
    elif d == 'C':
        res = [0, s * voxel_size[1], 0, 0]
    elif d == 'S':
        res = [s * voxel_size[0], 0, 0, 0]
    return res


def get_one_tile(views_images, grid_dim=None):
    # Building the tiled image
    image_size = (max([im.size[0] for im in views_images]),
                  max([im.size[1] for im in views_images]))
    if not grid_dim:
        grid_dim = {1: (1, 1),
                    2: (2, 1),
                    3: (3, 1),
                    4: (4, 1),
                    5: (5, 1),
                    6: (3, 2),
                    7: (7, 1),
                    8: (4, 2),
                    10: (10, 1),
                    12: (6, 2),
                    14: (7, 2),
                    16: (8, 2),
                    21: (7, 3),
                    24: (6, 4)}[len(views_images)]

    tiled_image = Image.new(
        'RGBA', (grid_dim[0] * image_size[0], grid_dim[1] * image_size[1]), 'black')
    positions = [[j * image_size[0], i * image_size[1]]
                 for i in six.moves.xrange(grid_dim[1])
                 for j in six.moves.xrange(grid_dim[0])]
    for i, pos in zip(views_images, positions):
        pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j])) /
               2.0 for j in six.moves.xrange(len(pos))]
        tiled_image.paste(i, (int(pos[0]), int(pos[1])))

    return tiled_image


def set_snap_layout(view_images):
    tiles = []
    for d in view_images.keys():
        tiles.append(get_one_tile(view_images[d]))
    geometry = (1, len(view_images))
    big_tile = get_one_tile(tiles, grid_dim=geometry)

    return big_tile
