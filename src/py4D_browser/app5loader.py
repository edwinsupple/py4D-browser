import h5py
import numpy as np
import xml.etree.ElementTree as ET
import py4DSTEM

def app5load(filename):
    if not filename.endswith('.app5'):
        raise ValueError('File format should be Nanomegas .app5')
    with h5py.File(filename) as f:
        metadata = f['Metadata'].asstr()[()]
        # print(f.keys())
        datasetid = -1
        datacube = None
        virtualstem = None
        blockname = 'noblock'
        root = ET.fromstring(metadata)
        metadict = {}

        createdtime = root.find('CreatedDateTime').text

        if root.find('FriendlyName').text == 'PED STEM/Series/Acquire':
            for item in root.findall('ProcedureData/Item'):
                if item.find('Name').text == 'VirtualStemImageResult':
                    virtualimageid = item.find('Value/Id').text
                    virtualstem = f[virtualimageid][:]
                if item.find('Name').text == 'Result':
                    datasetid = item.find('Value/Id').text
                if item.find('Name').text == 'BlockFileBaseName':
                    blockname = (item.find('Value').text)
                metadict[str(item.find('Name').text)] = item.find('Value').text

            if datasetid != -1:
                datacube = np.zeros((*virtualstem.shape, 256,256))
                for key in list(f[datasetid].keys()):

                    datacube[np.unravel_index(int(key), virtualstem.shape)] = f[datasetid][key]['Data']


    return [datacube, virtualstem, root, metadict, blockname+'_'+createdtime.replace(' ','_').replace('/', '_').replace(':', '-')]

def app5topy4dstem(filename, hot_pixel_limit=None):
    data, virtualstem, root, metadict, name = app5load(filename)

    datacube = py4DSTEM.DataCube(data)
    datacube.calibration.set_R_pixel_size(float(metadict['PointCollectionStepSize'])*1E9)
    datacube.calibration.set_R_pixel_units('nm')
    datacube.data = np.flip(datacube.data, axis=0)

    return [datacube, virtualstem, root, metadict, name]

# if __name__ == '__main__':
#     import matplotlib.pyplot as plt
#     import os
#     dirname = './240517_D315G/app5/'

#     for file in ['D315_10nm_4.5m_.05s_SS8_30umC2_05_17_2024_17-16-15.app5']:
#         print(file)
#         if file.endswith('.app5'):
#             data, virtualstem, metadata, filename = app5load(dirname+file)

    # plt.imshow(data[0,0])
    # plt.show()

