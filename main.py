import imageio
import utils as ut

def main():
    reader = imageio.get_reader('VideoBike.avi')
    fps = reader.get_meta_data()['fps']

    writer = imageio.get_writer('VideoDemo1.avi', fps=fps)

    i = 0
    for im in reader:

        if i > fps:
            break

        i += 1
        # aplica um slice para pegar apenas as intensidades resultando em
        # uma imagem inteira em preto e branco de cada frame
        data = im[:, :, 1]

        ut.segmentacao(data, 170)

        writer.append_data(data)

    writer.close()

main()