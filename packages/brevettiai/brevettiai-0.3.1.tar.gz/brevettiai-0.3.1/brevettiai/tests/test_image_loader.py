import unittest
import tensorflow as tf
import tensorflow_addons as tfa

from brevettiai.tests import get_resource


from brevettiai.data.image import ImagePipeline, ImageLoader, CropResizeProcessor


class TestCropResizeProcessor(unittest.TestCase):
    test_image_path = get_resource("0_1543413266626.bmp")

    def test_loader_affine_transform(self):
        image, _ = ImageLoader().load(self.test_image_path)

        processor = CropResizeProcessor(output_height=120, output_width=150,
                                        roi_vertical_offset=45, roi_horizontal_offset=37,
                                        interpolation="bilinear")

        # Run on processor
        img_out = processor.process(image)

        # Run with tfa.image.transform
        input_height, input_width = tf.shape(image)[:2]
        tr = tfa.image.transform_ops.matrices_to_flat_transforms(processor.affine_transform(input_height, input_width))
        img2 = tfa.image.transform(tf.cast(image, tf.float32), tf.cast(tr, tf.float32), processor.interpolation,
                                   output_shape=processor.output_size(input_height, input_width))

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(img_out - img2)), 5e-5)


class TestImagePipelineToImageLoaderConversion(unittest.TestCase):
    test_image_path = get_resource("0_1543413266626.bmp")

    def test_ensure_default_settings(self):
        ip = ImagePipeline()

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 0.0)

    def test_ensure_target_size(self):
        ip = ImagePipeline(target_size=(120, 150))

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 2.0)

    def test_ensure_roi(self):
        ip = ImagePipeline(rois=[[[10, 10], [50, 70]]])

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 0.0)

    def test_ensure_roi_and_target_size(self):
        ip = ImagePipeline(rois=[[[10, 10], [50, 70]]], target_size=(90, 70))

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 2.0)


if __name__ == '__main__':
    unittest.main()
