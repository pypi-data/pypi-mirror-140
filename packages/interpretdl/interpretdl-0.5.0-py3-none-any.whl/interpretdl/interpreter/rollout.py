
import numpy as np
import paddle
import re

from .abc_interpreter import Interpreter
from ..data_processor.readers import images_transform_pipeline, preprocess_save_path
from ..data_processor.visualizer import explanation_to_vis, show_vis_explanation, save_image


class RolloutInterpreter(Interpreter):
    """
    Rollout Interpreter.

    More details regarding the Rollout method can be found in the original paper:
    https://arxiv.org/abs/2005.00928
    """

    def __init__(self,
                 paddle_model,
                 use_cuda=None,
                 device='gpu:0') -> None:
        """

        Args:
            paddle_model (callable): A model with ``forward`` and possibly ``backward`` functions.
            device (str): The device used for running `paddle_model`, options: ``cpu``, ``gpu:0``, ``gpu:1`` etc.
            use_cuda (bool):  Would be deprecated soon. Use ``device`` directly.
        """
        Interpreter.__init__(self, paddle_model, device, use_cuda)
        self.paddle_prepared = False

        # init for usages during the interpretation.
        self.block_attns = []

    def interpret(self,
                  inputs,
                  start_layer=0,
                  resize_to=224, 
                  crop_to=None,
                  visual=True,
                  save_path=None):
        """
        Main function of the interpreter.

        Args:
            inputs (str or list of strs or numpy.ndarray): The input image filepath or a list of filepaths or numpy array of read images.
            labels (list or tuple or numpy.ndarray, optional): The target labels to analyze. The number of labels should be equal to the number of images. 
                If None, the most likely label for each image will be used. Default: None
            resize_to (int, optional): [description]. Images will be rescaled with the shorter edge being `resize_to`. Defaults to 224.
            crop_to ([type], optional): [description]. After resize, images will be center cropped to a square image with the size `crop_to`. 
                If None, no crop will be performed. Defaults to None.
            visual (bool, optional): Whether or not to visualize the processed image. Default: True
            save_path (str or list of strs or None, optional): The filepath(s) to save the processed image(s). If None, the image will not be saved. Default: None

        Returns:
            [numpy.ndarray]: interpretations/heatmap for images
        """

        imgs, data = images_transform_pipeline(inputs, resize_to, crop_to)
        bsz = len(data)  # batch size
        save_path = preprocess_save_path(save_path, bsz)

        if not self.paddle_prepared:
            self._paddle_prepare()

        blk_attns, preds = self.predict_fn(data)

        assert start_layer < len(blk_attns), "start_layer should be in the range of [0, num_block-1]"

        label = np.array(preds).reshape((bsz,))

        all_layer_attentions = []
        for attn_heads in blk_attns:
            avg_heads = (attn_heads.sum(axis=1) / attn_heads.shape[1]).detach()
            all_layer_attentions.append(avg_heads)

        # compute rollout between attention layers
        # adding residual consideration- code adapted from https://github.com/samiraabnar/attention_flow
        num_tokens = all_layer_attentions[0].shape[1]
        batch_size = all_layer_attentions[0].shape[0]
        eye = paddle.eye(num_tokens).expand((batch_size, num_tokens, num_tokens))
        all_layer_attentions = [all_layer_attentions[i] + eye for i in range(len(all_layer_attentions))]
        matrices_aug = [all_layer_attentions[i] / all_layer_attentions[i].sum(axis=-1, keepdim=True)
                            for i in range(len(all_layer_attentions))]
        joint_attention = matrices_aug[start_layer]
        for i in range(start_layer+1, len(matrices_aug)):
            joint_attention = matrices_aug[i].bmm(joint_attention)

        # rollout
        rollout_explanation = joint_attention[:, 0, 1:].reshape((-1, 14, 14)).cpu().detach().numpy()

        # visualization and save image.
        for i in range(bsz):
            vis_explanation = explanation_to_vis(imgs[i], rollout_explanation[i], style='overlay_heatmap')
            if visual:
                show_vis_explanation(vis_explanation)
            if save_path[i] is not None:
                save_image(save_path[i], vis_explanation)

        return rollout_explanation

    def _paddle_prepare(self, predict_fn=None):
        if predict_fn is None:
            paddle.set_device(self.device)
            # to get gradients, the ``train`` mode must be set.
            # we cannot set v.training = False for the same reason.
            self.paddle_model.train()

            # def hook for attention layer
            def hook(layer, input, output):
                self.block_attns.append(output)

            for n, v in self.paddle_model.named_sublayers():
                if re.match('^blocks.*.attn.attn_drop$', n):
                    # print(n)
                    v.register_forward_post_hook(hook)

                if "batchnorm" in v.__class__.__name__.lower():
                    v._use_global_stats = True
                if "dropout" in v.__class__.__name__.lower():
                    v.p = 0

                # Report issues or pull requests if more layers need to be added.

            def predict_fn(data):
                data = paddle.to_tensor(data)
                data.stop_gradient = False
                self.block_attns = []
                out = self.paddle_model(data)
                out = paddle.nn.functional.softmax(out, axis=1)
                preds = paddle.argmax(out, axis=1)
                label = preds.numpy()

                return self.block_attns, label

        self.predict_fn = predict_fn
        self.paddle_prepared = True
