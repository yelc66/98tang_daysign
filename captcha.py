import base64
import json
from io import BytesIO
import cv2
import numpy as np
from PIL import Image, ImageDraw


__DEBUG__ = False


class CaptchaError(Exception):
    pass


class PuzzleCaptchaSolver:
    def __init__(self, gap_image, bg_image):
        self.gap_image = self.convert_to_cv_img(gap_image)
        self.bg_image = self.convert_to_cv_img(bg_image)

    @staticmethod
    def convert_to_cv_img(img):
        pil_img = img.convert("RGBA")
        cv_img = np.array(pil_img)
        return cv2.cvtColor(cv_img, cv2.COLOR_RGBA2BGRA)

    @staticmethod
    def convert_to_pil_img(img):
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    def remove_whitespace(self, img):
        """

        This method removes whitespace from an image by cropping it to the area containing non-whitespace pixels.

        :param img: The input image.
        :return: An image array representing the cropped image without whitespace.

        """
        min_x, min_y, max_x, max_y = 255, 255, 0, 0
        rows, cols, channel = img.shape
        for x in range(1, rows):
            for y in range(1, cols):
                if len(set(img[x, y])) >= 2:
                    min_x, min_y = min(x, min_x), min(y, min_y)
                    max_x, max_y = max(x, max_x), max(y, max_y)
        whitespace_removed_img = img[min_x:max_x, min_y:max_y]
        return whitespace_removed_img

    def apply_edge_detection(self, img):
        """
        Applies edge detection on the given image.

        :param img: The input image.
        :return: The image with edges highlighted.
        """
        grayscale_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale_img, 100, 200)
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        return edges_rgb

    def find_position_of_puzzle(self, puzzle_pic, background_pic):
        """
        Find the position of the puzzle on the background picture.

        :param puzzle_pic: The puzzle picture to find.
        :type puzzle_pic: numpy.ndarray
        :param background_pic: The background picture to search in.
        :type background_pic: numpy.ndarray
        :return: The coordinate of the top-left corner of the puzzle in the background picture.
        :rtype: int
        """
        tpl_height, tpl_width = puzzle_pic.shape[:2]
        result = cv2.matchTemplate(
            background_pic, puzzle_pic, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        tl = max_loc
        br = (tl[0] + tpl_width, tl[1] + tpl_height)
        cv2.rectangle(background_pic, tl, br, (0, 0, 255), 2)
        if __DEBUG__:
            self.convert_to_pil_img(background_pic).show()
        return tl

    def discern(self) -> tuple[int, int]:
        """
        Performs the discernment process to find the position of the puzzle in the given images.

        :return: The position of the puzzle in the images.
        """
        # gap_image = self.remove_whitespace(self.gap_image)
        edge_detected_gap = self.apply_edge_detection(self.gap_image)
        edge_detected_bg = self.apply_edge_detection(self.bg_image)
        puzzle_position = self.find_position_of_puzzle(
            edge_detected_gap, edge_detected_bg)
        return puzzle_position


def decode_img_url(s: str) -> Image:
    header, encoded = s.split(",", 1)
    assert header.startswith("data:image")
    image = Image.open(BytesIO(
        base64.b64decode(encoded)))
    return image


def center_circle_crop_with_alpha(master: Image.Image, thumb: Image.Image) -> Image:
    # Convert to RGBA for transparency
    master = master.convert("RGBA")

    target_w, target_h = thumb.size
    w, h = master.size

    # Center crop
    cx, cy = w // 2, h // 2
    half_w, half_h = target_w // 2, target_h // 2

    left = cx - half_w
    upper = cy - half_h
    right = left + target_w
    lower = upper + target_h

    cropped = master.crop((left, upper, right, lower))

    # Create circular alpha mask
    mask = Image.new("L", (target_w, target_h), 0)
    draw = ImageDraw.Draw(mask)

    radius = min(target_w, target_h) // 2
    center = (target_w // 2, target_h // 2)

    draw.ellipse(
        (
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ),
        fill=255
    )

    # Apply mask as alpha channel
    cropped.putalpha(mask)

    return cropped


def masked_mse(a_rgba: Image.Image, b_rgba: Image.Image) -> float:
    """
    Mean squared error comparing RGB only where BOTH images are opaque (alpha > 0).
    Lower = more similar.
    """
    a = np.asarray(a_rgba.convert("RGBA"), dtype=np.float32)
    b = np.asarray(b_rgba.convert("RGBA"), dtype=np.float32)

    # mask where both are visible
    mask = (a[..., 3] > 0) & (b[..., 3] > 0)
    if not np.any(mask):
        return float("inf")

    diff = a[..., :3] - b[..., :3]              # RGB diff
    diff2 = np.sum(diff * diff, axis=2)         # per-pixel squared error (RGB)
    return float(diff2[mask].mean())


def find_best_rotation(master: Image.Image,
                       thumb: Image.Image,
                       step_deg: int = 1,
                       max_deg: int = 360) -> tuple[int, bool]:
    thumb_rgba = thumb.convert("RGBA")

    best_img = None
    best_deg = None
    best_score = float("inf")

    for deg in range(0, max_deg, step_deg):
        rotated = master.rotate(
            deg,
            resample=Image.BICUBIC,
            expand=False,
        )

        score = masked_mse(rotated, thumb_rgba)
        if score < best_score:
            best_score = score
            best_deg = deg
            best_img = rotated

    if __DEBUG__:
        best_img.show()
    return best_deg, best_score


def resolve_captcha(data: dict) -> str:
    master = decode_img_url(data["data"]["master_image_base64"])
    thumb = decode_img_url(data["data"]["thumb_image_base64"])
    _type = data["data"]["type"]

    match _type:
        case "rotate":
            cropped = center_circle_crop_with_alpha(master, thumb)

            if __DEBUG__:
                thumb.show()
                # cropped.show()

            deg, _ = find_best_rotation(cropped, thumb)
            print(f"Matched at {deg} degrees")

            return str(deg)

        case "slide" | "drag":
            if __DEBUG__:
                master.show()

            solver = PuzzleCaptchaSolver(
                gap_image=thumb,
                bg_image=master,
            )
            position = solver.discern()
            print(f"The position of the puzzle is: {position}")

            if _type == "slide":
                position = (position[0],
                            data["data"]["display_y"])

            return f'{position[0]},{position[1]}'

        case "click":
            raise CaptchaError("click not supported")

        case _:
            raise CaptchaError("unknown captcha type")


def main():
    global __DEBUG__
    __DEBUG__ = True

    # with open("captcha_rotate.json") as f:
    #     response = json.load(f)
    # resolve_captcha(response)

    # with open("captcha_drag.json") as f:
    #     response = json.load(f)
    # resolve_captcha(response)

    # with open("captcha_slide.json") as f:
    #     response = json.load(f)
    # resolve_captcha(response)

    with open("captcha_debug.json") as f:
        response = json.load(f)
    resolve_captcha(response)


if __name__ == "__main__":
    main()
