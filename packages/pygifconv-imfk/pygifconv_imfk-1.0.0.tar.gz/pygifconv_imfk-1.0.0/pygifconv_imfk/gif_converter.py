import glob
from PIL import Image


class GifConverter:

    def __init__(self, path_in=None, path_out=None, resize=(320, 240)):
        """
        :param path_in: original images path(Ex: images/*.png)
        :param path_out: result GIF path
        :param resize: resizing
        """
        self.path_in = path_in or "./*.png"  # None이 들어오면 "./*.png"가 들어온다.
        self.path_out = path_out or "./output.gif"
        self.resize = resize

    def convert_gif(self):
        """
        GIF 이미지 변환 기능 수행 !!
        """
        print(self.path_in, self.path_out, self.resize)

        img, *images = \
            [Image.open(f).resize((320, 420), Image.ANTIALIAS) for f in sorted(glob.glob(self.path_in))]\

        try:
            img.save(
                fp=self.path_out,
                format="GIF",
                append_images=images,
                save_all=True,
                duration=300,
                loop=0
            )
        except IOError:
            print("Cannot convert!", img)


if __name__ == "__main__":
    # 클래스
    c = GifConverter("../project/images/*.png", "../project/image_out/result.gif")

    # 변환
    c.convert_gif()

    print(c.convert_gif.__doc__)
