from log import log
import re


class ParsedNote:
    def __init__(self, content, need_upload_images):
        self.content = content
        self.need_upload_images = need_upload_images

    def replace_image_url(self, origin_img_image_url_map: dict[str, str]):
        """
        替换md文件中的图片链接中的地址
        :param origin_img_image_url_map:
        :return:
        """
        log.info(f'需要上传的图片集合：{self.need_upload_images}')
        for img_name in self.need_upload_images:
            if img_name not in origin_img_image_url_map:
                log.info(f'图片：{img_name} 不存在')
                continue
            self.content = self.content.replace(f'(index_files/{img_name})', f'({origin_img_image_url_map[img_name]})')
            self.content = self.content.replace(f'({img_name})', f'({origin_img_image_url_map[img_name]})')