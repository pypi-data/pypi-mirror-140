import torch
import torch.nn as nn

from torch import nn
import inspect
from functools import partial

# import commons




# base_model

from abc import ABCMeta,abstractmethod
import torch
import numpy as np
from collections import OrderedDict
import torch.distributed as dist

import torch.nn as nn
# from SOHO.utils import print_log

def print_log(*args, **kwargs):
    print(args)
    print(kwargs)

class BaseModel(nn.Module,metaclass=ABCMeta):
    def __init__(self):
        super(BaseModel, self).__init__()
        pass

    @property
    def with_neck(self):
        """
        whether the model has a neck
        :return:
        """
        return hasattr(self,"neck") and self.neck is not None

    @property
    def with_head(self):
        return hasattr(self, 'head') and self.head is not None

    def init_weights(self, pretrained=None):
        if pretrained is not None:
            print_log('load model from: {}'.format(pretrained), logger='root')

    @abstractmethod
    def forward_backbone(self,img):
        """Forward backbone
                Returns:
                    x (tuple): backbone outputs
                """
        pass

    @abstractmethod
    def forward_train(self, img, gt_label, **kwargs):
        pass

    @abstractmethod
    def forward_test(self, img, **kwargs):
        pass

    def forward(self, img, mode='train', **kwargs):
        if mode == 'train':
            return self.forward_train(img, **kwargs)
        elif mode == 'test':
            return self.forward_test(img, **kwargs)
        elif mode == 'extract':
            return self.forward_backbone(img)
        else:
            raise Exception("No such mode: {}".format(mode))

    def _parse_losses(self, losses):
        """Parse the raw outputs (losses) of the network.
        Args:
            losses (dict): Raw output of the network, which usually contain
                losses and other necessary infomation.
        Returns:
            tuple[Tensor, dict]: (loss, log_vars), loss is the loss tensor
                which may be a weighted sum of all losses, log_vars contains
                all the variables to be sent to the logger.
        """
        log_vars = OrderedDict()
        for loss_name, loss_value in losses.items():
            if isinstance(loss_value, torch.Tensor):
                log_vars[loss_name] = loss_value.mean()
            elif isinstance(loss_value, list):
                log_vars[loss_name] = sum(_loss.mean() for _loss in loss_value)
            else:
                raise TypeError(
                    f'{loss_name} is not a tensor or list of tensors')

        loss = sum(_value for _key, _value in log_vars.items()
                   if 'loss' in _key)

        log_vars['loss'] = loss
        for loss_name, loss_value in log_vars.items():
            # reduce loss when distributed training
            if dist.is_available() and dist.is_initialized():
                loss_value = loss_value.data.clone()
                dist.all_reduce(loss_value.div_(dist.get_world_size()))
            log_vars[loss_name] = loss_value.item()

        return loss, log_vars

    def train_step(self, data, optimizer):
        """The iteration step during training.
        This method defines an iteration step during training, except for the
        back propagation and optimizer updating, which are done in an optimizer
        hook. Note that in some complicated cases or models, the whole process
        including back propagation and optimizer updating are also defined in
        this method, such as GAN.
        Args:
            data (dict): The output of dataloader.
            optimizer (:obj:`torch.optim.Optimizer` | dict): The optimizer of
                runner is passed to ``train_step()``. This argument is unused
                and reserved.
        Returns:
            dict: It should contain at least 3 keys: ``loss``, ``log_vars``,
                ``num_samples``.
                ``loss`` is a tensor for back propagation, which can be a
                weighted sum of multiple losses.
                ``log_vars`` contains all the variables to be sent to the
                logger.
                ``num_samples`` indicates the batch size (when the model is
                DDP, it means the batch size on each GPU), which is used for
                averaging the logs.
        """
        losses = self(**data)
        loss, log_vars = self._parse_losses(losses)

        outputs = dict(
            loss=loss, log_vars=log_vars, num_samples=len(data['img'].data))

        return outputs

    def val_step(self, data, optimizer):
        """The iteration step during validation.
        This method shares the same signature as :func:`train_step`, but used
        during val epochs. Note that the evaluation after training epochs is
        not implemented with this method, but an evaluation hook.
        """
        losses = self(**data)
        loss, log_vars = self._parse_losses(losses)

        outputs = dict(
            loss=loss, log_vars=log_vars, num_samples=len(data['img'].data))

        return outputs


class Registry(object):

    def __init__(self, name):
        self._name = name
        self._module_dict = dict()

    def __repr__(self):
        format_str = self.__class__.__name__ + '(name={}, items={})'.format(
            self._name, list(self._module_dict.keys()))
        return format_str

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        return self._module_dict.get(key, None)

    def _register_module(self, module_class, force=False):
        """Register a module.
        Args:
            module (:obj:`nn.Module`): Module to be registered.
        """
        if not inspect.isclass(module_class):
            raise TypeError('module must be a class, but got {}'.format(
                type(module_class)))
        module_name = module_class.__name__
        if not force and module_name in self._module_dict:
            raise KeyError('{} is already registered in {}'.format(
                module_name, self.name))
        self._module_dict[module_name] = module_class

    def register_module(self, cls=None, force=False):
        if cls is None:
            return partial(self.register_module, force=force)
        self._register_module(cls, force=force)
        return cls


def build_from_cfg(cfg, registry, default_args=None):
    """Build a module from config dict.
    Args:
        cfg (dict): Config dict. It should at least contain the key "type".
        registry (:obj:`Registry`): The registry to search the type from.
        default_args (dict, optional): Default initialization arguments.
    Returns:
        obj: The constructed object.
    """
    assert isinstance(cfg, dict) and 'type' in cfg
    assert isinstance(default_args, dict) or default_args is None
    args = cfg.copy()
    obj_type = args.pop('type')
    if isinstance(obj_type, str):
        obj_cls = registry.get(obj_type)
        if obj_cls is None:
            raise KeyError('{} is not in the {} registry'.format(
                obj_type, registry.name))
    elif inspect.isclass(obj_type):
        obj_cls = obj_type
    else:
        raise TypeError('type must be a str or valid type, but got {}'.format(
            type(obj_type)))
    if default_args is not None:
        for name, value in default_args.items():
            args.setdefault(name, value)
    return obj_cls(**args)

## builder.py


MODELS = Registry('model')
BACKBONES = Registry('backbone')
LANGUAGE= Registry('language')
NECKS = Registry('neck')
HEADS = Registry('head')
LOSSES = Registry('loss')


def build(cfg, registry, default_args=None):
    if isinstance(cfg, list):
        modules = [
            build_from_cfg(cfg_, registry, default_args) for cfg_ in cfg
        ]
        return nn.Sequential(*modules)
    else:
        return build_from_cfg(cfg, registry, default_args)


def build_backbone(cfg):
    return build(cfg, BACKBONES)

def build_language(cfg):
    return build(cfg,LANGUAGE)


def build_neck(cfg):
    return build(cfg, NECKS)


def build_head(cfg):
    return build(cfg, HEADS)


def build_loss(cfg):
    return build(cfg, LOSSES)


def build_model(cfg):
    return build(cfg, MODELS)

@MODELS.register_module
class SOHOSingleStreamVQA(BaseModel):
    def __init__(self,
                 backbone,
                 neck=None,
                 language=None,
                 head=None,
                 backbone_pre=None,
                 language_pre=None):
        super(SOHOSingleStreamVQA, self).__init__()

        self.backbone = build_backbone(backbone)
        if neck is not None:
            self.neck = build_neck(neck)
        else:
            self.neck = None

        if language is not None:
            self.language = build_language(language)
        else:
            self.language=None

        if head is not None:
            self.head = build_head(head)
        else:
            self.head = None


        self.init_weights(backbone_pre,language_pre)


    def init_weights(self, backbone_pre=None,language_pre=None):
        if backbone_pre is not None:
            print('load model from: {}'.format(backbone_pre), logger='root')

        self.backbone.init_weights(pretrained=backbone_pre)
        if self.neck:
            self.neck.init_weights()

        if self.language and language_pre is not None:
            print('load language model from: {}'.format(language_pre), logger='root')
        self.language.init_weights(pretrained=language_pre)

        if self.head:
            self.head.init_weights()

    def forward_backbone(self,img):
        x = self.backbone(img)
        return x

    def forward_train(self, img, language_tokens,language_attention,vqa_labels,img_meta, **kwargs):
        bs = img.size(0)
        x = self.forward_backbone(img)
        num_sentence = language_tokens[0].size(0)
        language_tokens = torch.cat(language_tokens,dim=0)
        language_attention = torch.cat(language_attention,dim=0)
        vqa_labels = torch.cat(vqa_labels,dim=0)

        assert language_tokens.size(0) ==bs*num_sentence


        visual_tokens, visual_attention = self.neck(x,img_meta)

        fusion_feature=self.language(language_tokens,language_attention,
                                     visual_tokens=visual_tokens,visual_attention_mask=visual_attention)

        next_pred=self.head(fusion_feature)
        losses=self.head.loss(next_pred,vqa_labels)
        return losses

    def forward_test(self, img, language_tokens,language_attention,img_meta,vqa_labels=None,question_ids=None, **kwargs):
        bs = img.size(0)
        x = self.forward_backbone(img)
        num_sentence = language_tokens[0].size(0)
        language_tokens = torch.cat(language_tokens, dim=0)
        language_attention = torch.cat(language_attention, dim=0)

        assert language_tokens.size(0) == bs * num_sentence


        visual_tokens, visual_attention = self.neck(x,img_meta)

        fusion_feature = self.language(language_tokens, language_attention,
                                       visual_tokens=visual_tokens, visual_attention_mask=visual_attention)

        next_pred = self.head(fusion_feature)
        outs=[question_ids[0],next_pred]
        keys=["ids","pred"]
        out_tensors = [out.cpu() for out in outs]
        return dict(zip(keys,out_tensors))
