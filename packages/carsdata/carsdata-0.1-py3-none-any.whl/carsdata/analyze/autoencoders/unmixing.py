from typing import Union, Sequence, Optional
from math import pi
import numpy as np
import torch
from torch import nn, Tensor
from carsdata.analyze.autoencoders.normalizer import normalizer_factory
from carsdata.utils.math import gaussian


class _EncoderBlock(nn.Module):
    def __init__(
        self, dim: int, input_channels: int, output_channels: int, filters_size: Union[int, Sequence[int]],
        activation: Optional[str], pooling_type: Optional[str] = None, pooling_size: Union[int, Sequence[int]] = 0,
        padding: Union[str, int, Sequence[int]] = 0, padding_mode: str = 'zeros', bias: bool = True
    ) -> None:
        super().__init__()
        self.conv = getattr(nn, f'Conv{dim}d')(input_channels, output_channels, filters_size, padding=padding,
                                               padding_mode=padding_mode, bias=bias)
        if pooling_type is not None:
            self.pooling = getattr(nn, f'{pooling_type.capitalize()}Pool{dim}d')(pooling_size)
        else:
            self.pooling = None
        self.normalizer = getattr(nn, f'BatchNorm{dim}d')(output_channels)
        if activation is not None:
            self.activation = getattr(nn, activation)()
        else:
            self.activation = None
        if dim == 1:
            self.dropout = nn.Dropout(0.2)
        else:
            self.dropout = getattr(nn, f'Dropout{dim}d')(0.2)

    def forward(self, x: Tensor) -> Tensor:
        x = self.conv(x)
        if self.pooling is not None:
            x = self.pooling(x)
        x = self.normalizer(x)
        if self.activation is not None:
            x = self.activation(x)
        # x = self.dropout(x)
        return x


class _SpectralEncoderBlock(_EncoderBlock):
    def __init__(
        self, input_channels: int, output_channels: int, filters_size: int, activation: Optional[str],
        pooling_type: str, pooling_size: int
    ) -> None:
        super().__init__(1, input_channels, output_channels, filters_size, activation, pooling_type=pooling_type,
                         pooling_size=pooling_size)


class _SpatialEncoderBlock(_EncoderBlock):
    def __init__(
        self, input_channels: int, output_channels: int, filters_size: Union[int, Sequence[int]],
        activation: Optional[str], padding_mode: str, bias: bool
    ) -> None:
        super().__init__(2, input_channels, output_channels, filters_size, activation, padding='same',
                         padding_mode=padding_mode, bias=bias)


class _DenseBlock(nn.Module):

    def __init__(
        self, input_channels: int, output_channels: int, activation: Optional[str] = None, bias: bool = True
    ) -> None:
        super().__init__()
        self.dense = nn.Linear(input_channels, output_channels, bias)
        if activation is not None:
            self.activation = getattr(nn, activation)()
        else:
            self.activation = None
        self.normalizer = nn.BatchNorm1d(output_channels)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x: Tensor) -> Tensor:
        input_shape = x.shape
        x = self.dense(x)
        x = torch.reshape(x, (np.prod(input_shape[:-1]), x.shape[-1]))
        x = self.normalizer(x)
        x = torch.reshape(x, (*input_shape[:-1], x.shape[-1]))
        if self.activation is not None:
            x = self.activation(x)
        #x = self.dropout(x)
        return x


class DenseUnmixing(nn.Module):
    def __init__(
        self, spectra_length: int, features: Sequence[int], activations: Optional[Sequence[str]] = None,
        normalizer: Union[nn.Module, dict] = None, init_decoder: str = 'random'
    ) -> None:
        super().__init__()
        self.encoder = []
        for idx, feature in enumerate(features):
            in_features = spectra_length if idx == 0 else self.encoder[-1].dense.out_features
            bias = idx == len(features)-1
            activation = None if activations is None else activations[idx]
            self.encoder.append(_DenseBlock(in_features, feature, activation, bias))
        self.encoder = nn.Sequential(*self.encoder)
        self.conc_normalizer = nn.Softmax(dim=-1)

        self.decoder = nn.Linear(features[-1], spectra_length, bias=False)
        if init_decoder == 'zero' or init_decoder == 'gaussian':
            with torch.no_grad():
                peaks = torch.zeros((features[-1], spectra_length))
                if init_decoder == 'gaussian':
                    for peak_idx in range(len(peaks)):
                        center = torch.randint(spectra_length, (1,))[0]
                        width = 10
                        peaks[peak_idx] = gaussian(spectra_length, center, width)
                self.decoder.weight.copy_(peaks.T)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.spectr_normalizer = normalizer
        #with torch.no_grad():
        #    peaks = torch.zeros((features[-1], spectra_length))
        #    for peak_idx in range(len(peaks)):
        #        center = torch.randint(spectra_length, (1,))[0]
        #        width = 10
        #        peaks[peak_idx] = 1. / (width * torch.sqrt(Tensor([2. * pi]))) * torch.exp(
        #                        - (torch.arange(spectra_length) - center) ** 2 / (2. * width ** 2))
        #    self.decoder.weight.copy_(peaks.T)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        self.concentrations = self.encoder(x)
        self.concentrations = self.conc_normalizer(self.concentrations)
        reconstructed = self.decoder(self.concentrations)
        if self.spectr_normalizer is not None:
            reconstructed = self.spectr_normalizer(reconstructed)

        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class CascadeUnmixing(nn.Module):
    def __init__(
            self, spectra_length: int, first_features: Sequence[int], second_features: Sequence[int],
            first_activations: Optional[Sequence[str]] = None, second_activations: Optional[Sequence[str]] = None,
            normalizer: Union[nn.Module, dict] = nn.Softmax(-1)
    ) -> None:
        super().__init__()
        self.first_encoder = []
        for idx, feature in enumerate(first_features):
            in_features = spectra_length if idx == 0 else self.first_encoder[-1].dense.out_features
            bias = idx == len(first_features) - 1
            activation = None if first_activations is None else first_activations[idx]
            self.first_encoder.append(_DenseBlock(in_features, feature, activation, bias))
        self.first_encoder = nn.Sequential(*self.first_encoder)
        self.first_decoder = nn.Linear(first_features[-1], spectra_length)

        self.second_encoder = []
        for idx, feature in enumerate(second_features):
            in_features = spectra_length if idx == 0 else self.second_features[-1].dense.out_features
            bias = idx == len(second_features) - 1
            activation = None if second_activations is None else second_activations[idx]
            self.second_encoder.append(_DenseBlock(in_features, feature, activation, bias))
        self.second_encoder = nn.Sequential(*self.second_encoder)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.normalizer = normalizer
        self.decoder = nn.Linear(second_features[-1], spectra_length, bias=False)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        first_latent = self.first_encoder(x)
        reconstructed = self.first_decoder(first_latent)
        self.concentrations = self.second_encoder(reconstructed)
        self.concentrations = self.normalizer(self.concentrations)
        reconstructed = self.decoder(self.concentrations)
        # reconstructed = self.normalizer(reconstructed)
        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class SpectralUnmixing(nn.Module):
    def __init__(
        self, spectra_length: int, nb_components: int, features: Sequence[int], filters: Sequence[int],
        activations: Sequence[Optional[str]], pooling_types: Sequence[str], pooling_sizes: Sequence[int],
        normalizer: Union[nn.Module, dict] = nn.Softmax(-1)
    ) -> None:
        super().__init__()
        self.blocks = []
        for feature, filter_size, activation, pooling_type, pooling_size in zip(features, filters, activations,
                                                                                pooling_types, pooling_sizes):
            if len(self.blocks) == 0:
                self.blocks.append(_SpectralEncoderBlock(1, feature, filter_size, activation, pooling_type,
                                                        pooling_size))
            else:
                self.blocks.append(_SpectralEncoderBlock(self.blocks[-1].conv.out_channels, feature, filter_size,
                                                        activation, pooling_type, pooling_size))
        self.features_extractor = nn.Sequential(*self.blocks)
        dummy_spectra = torch.zeros((1, 1, spectra_length))
        dummy_spectra = self.features_extractor(dummy_spectra)
        features_shape = (np.prod(dummy_spectra.shape[-2:])).item()
        self.encoder = nn.Linear(features_shape, nb_components, bias=False)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.normalizer = normalizer
        self.decoder = nn.Linear(nb_components, spectra_length, bias=False)
        #with torch.no_grad():
        #    peaks = torch.zeros((nb_components, spectra_length))
        #    for peak_idx in range(len(peaks)):
        #        center = torch.randint(spectra_length, (1,))[0]
        #        width = 10
        #        peaks[peak_idx] = 1. / (width * torch.sqrt(Tensor([2. * pi]))) * torch.exp(
        #            - (torch.arange(spectra_length) - center) ** 2 / (2. * width ** 2))
        #    self.decoder.weight.copy_(peaks.T)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        linearized_shape = np.prod(x.shape[:-1]).item()
        linearized = torch.reshape(x, (linearized_shape, 1, x.shape[-1]))
        spectral_features = self.features_extractor(linearized)
        features_concat_shape = np.prod(spectral_features.shape[-2:]).item()
        features_map = torch.reshape(spectral_features, (*x.shape[:-1], features_concat_shape))
        self.concentrations = self.encoder(features_map)
        self.concentrations = self.normalizer(self.concentrations)
        reconstructed = self.decoder(self.concentrations)
        reconstructed = self.normalizer(reconstructed)
        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class DenseSpectralSpatial(nn.Module):
    def __init__(
        self, spectra_length: int, spectral_features: Sequence[int], spectral_activations: Sequence[Optional[str]],
        spatial_features: Sequence[int], spatial_filters: Sequence[Union[int, Sequence[int]]],
        spatial_activations: Sequence[Optional[str]], padding_modes: Sequence[str],
        normalizer: Union[nn.Module, dict] = nn.Softmax2d(), init_decoder: str = 'random'
    ) -> None:
        super().__init__()
        self.spectral_blocks = []
        for feature, activation in zip(spectral_features, spectral_activations):
            first_block = len(self.spectral_blocks) == 0
            in_features = spectra_length if first_block else self.spectral_blocks[-1].dense.out_features
            self.spectral_blocks.append(_DenseBlock(in_features, feature, activation, bias=True))
        self.spectral_encoder = nn.Sequential(*self.spectral_blocks)
        self.spatial_blocks = []
        for feature, filter_size, activation, padding_mode in zip(spatial_features, spatial_filters,
                                                                  spatial_activations, padding_modes):
            first_block = len(self.spatial_blocks) == 0
            in_features = spectral_features[-1] if first_block else self.spatial_blocks[-1].conv.out_channels
            bias = len(self.spatial_blocks) == len(spatial_features) - 1
            self.spatial_blocks.append(_SpatialEncoderBlock(in_features, feature, filter_size, activation,
                                                            padding_mode, bias=bias))
        self.spatial_encoder = nn.Sequential(*self.spatial_blocks)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.normalizer = normalizer
        self.decoder = nn.Linear(spatial_features[-1], spectra_length, bias=False)
        if init_decoder == 'zero' or init_decoder == 'gaussian':
            with torch.no_grad():
                peaks = torch.zeros((spatial_features[-1], spectra_length))
                if init_decoder == 'gaussian':
                    for peak_idx in range(len(peaks)):
                        center = torch.randint(spectra_length, (1,))[0]
                        width = 10
                        peaks[peak_idx] = gaussian(spectra_length, center, width)
                self.decoder.weight.copy_(peaks.T)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        spectral_features = self.spectral_encoder(x)
        # Need to move dimensions to have features after batch dim
        features_map = torch.movedim(spectral_features, (1, 2, 3), (2, 3, 1))
        self.concentrations = self.spatial_encoder(features_map)
        self.concentrations = self.normalizer(self.concentrations)
        # Need to move dimensions to have features at the end for Dense layer
        self.concentrations = torch.movedim(self.concentrations, (1, 2, 3), (3, 1, 2))
        reconstructed = self.decoder(self.concentrations)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (2, 3, 1))
        reconstructed = self.normalizer(reconstructed)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (3, 1, 2))
        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class SpatialUnmixing(nn.Module):
    def __init__(
        self, spectra_length: int, features: Sequence[int], filters: Sequence[Union[int, Sequence[int]]],
        activations: Sequence[Optional[str]], padding_modes: Sequence[str],
        normalizer: Optional[Union[nn.Module, dict]] = None, init_decoder: str = 'random'
    ) -> None:
        super().__init__()
        self.blocks = []
        for feature, filter_size, activation, padding_mode in zip(features, filters, activations, padding_modes):
            if len(self.blocks) == 0:
                self.blocks.append(_SpatialEncoderBlock(spectra_length, feature, filter_size, activation,
                                                        padding_mode, bias=True))
            elif len(self.blocks) == len(features)-2:
                self.blocks.append(
                    _SpatialEncoderBlock(self.blocks[-1].conv.out_channels, feature, filter_size,
                                         activation, padding_mode, bias=False))
            else:
                self.blocks.append(_SpatialEncoderBlock(self.blocks[-1].conv.out_channels, feature, filter_size,
                                                        activation, padding_mode, bias=True))
        self.encoder = nn.Sequential(*self.blocks)
        self.conc_normalizer = nn.Softmax2d()

        self.decoder = nn.Linear(features[-1], spectra_length, bias=False)
        if init_decoder == 'zero' or init_decoder == 'gaussian':
            with torch.no_grad():
                peaks = torch.zeros((features[-1], spectra_length))
                if init_decoder == 'gaussian':
                    for peak_idx in range(len(peaks)):
                        center = torch.randint(spectra_length, (1,))[0]
                        width = 10
                        peaks[peak_idx] = gaussian(spectra_length, center, width)
                self.decoder.weight.copy_(peaks.T)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.spectr_normalizer = normalizer
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        x = torch.movedim(x, (1, 2, 3), (2, 3, 1))
        self.concentrations = self.encoder(x)
        self.concentrations = self.conc_normalizer(self.concentrations)
        self.concentrations = torch.movedim(self.concentrations, (1, 2, 3), (3, 1, 2))
        reconstructed = self.decoder(self.concentrations)
        # reconstructed = torch.movedim(reconstructed, (1, 2, 3), (2, 3, 1))
        # if self.normalizer is not None:
        #     reconstructed = self.normalizer(reconstructed)
        if self.spectr_normalizer is not None:
            reconstructed = self.spectr_normalizer(reconstructed)
        # reconstructed = torch.movedim(reconstructed, (1, 2, 3), (3, 1, 2))
        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class SpectralSpatialUnmixing(nn.Module):
    """
    Convolutional AE with a spectral features extractor and spatial dimensionality reduction for unmixing.
    """
    def __init__(
        self, spectra_length: int, spectral_features: Sequence[int], spectral_filters: Sequence[int],
        spectral_activations: Sequence[str], pooling_types: Sequence[str], pooling_sizes: Sequence[int],
        spatial_features: Sequence[int], spatial_filters: Sequence[Union[int, Sequence[int]]],
        spatial_activations: Sequence[str], padding_modes: Sequence[str],
        normalizer: Union[nn.Module, dict] = nn.Softmax2d(),
    ) -> None:
        super().__init__()
        self.spectral_blocks = []
        for feature, filter_size, activation, pooling_type, pooling_size in zip(spectral_features, spectral_filters,
                                                                                spectral_activations, pooling_types,
                                                                                pooling_sizes):
            if len(self.spectral_blocks) == 0:
                self.spectral_blocks.append(_SpectralEncoderBlock(1, feature, filter_size, activation, pooling_type,
                                                                 pooling_size))
            else:
                self.spectral_blocks.append(_SpectralEncoderBlock(self.spectral_blocks[-1].conv.out_channels, feature,
                                                                 filter_size, activation, pooling_type, pooling_size))
        self.spectral_encoder = nn.Sequential(*self.spectral_blocks)
        dummy_spectra = torch.zeros((1, 1, spectra_length))
        dummy_spectra = self.spectral_encoder(dummy_spectra)
        features_shape = np.prod(dummy_spectra.shape[-2:]).item()
        self.spatial_blocks = []
        for feature, filter_size, activation, padding_mode in zip(spatial_features, spatial_filters,
                                                                  spatial_activations, padding_modes):
            if len(self.spatial_blocks) == 0:
                self.spatial_blocks.append(_SpatialEncoderBlock(features_shape, feature, filter_size, activation,
                                                                padding_mode, bias=True))
            elif len(self.spatial_blocks) == len(spatial_features)-2:
                self.spatial_blocks.append(
                    _SpatialEncoderBlock(self.spatial_blocks[-1].conv.out_channels, feature, filter_size,
                                         activation, padding_mode, bias=False))
            else:
                self.spatial_blocks.append(_SpatialEncoderBlock(self.spatial_blocks[-1].conv.out_channels, feature,
                                                                filter_size, activation, padding_mode, bias=True))
        self.spatial_encoder = nn.Sequential(*self.spatial_blocks)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.normalizer = normalizer
        self.decoder = nn.Linear(spatial_features[-1], spectra_length, bias=False)
        with torch.no_grad():
            peaks = torch.zeros((spatial_features[-1], spectra_length))
        #    for peak_idx in range(len(peaks)):
        #        center = torch.randint(spectra_length, (1,))[0]
        #        width = 10
        #        peaks[peak_idx] = gaussian(spectra_length, center, width)
            self.decoder.weight.copy_(peaks.T)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        linearized_shape = np.prod(x.shape[:-1]).item()
        linearized = torch.reshape(x, (linearized_shape, 1, x.shape[-1]))
        spectral_features = self.spectral_encoder(linearized)
        features_concat_shape = np.prod(spectral_features.shape[-2:]).item()
        features_map = torch.reshape(spectral_features, (*x.shape[:-1], features_concat_shape))
        # Need to move dimensions to have features after batch dim
        features_map = torch.movedim(features_map, (1, 2, 3), (2, 3, 1))
        self.concentrations = self.spatial_encoder(features_map)
        self.concentrations = self.normalizer(self.concentrations)
        # Need to move dimensions to have features at the end for Dense layer
        self.concentrations = torch.movedim(self.concentrations, (1, 2, 3), (3, 1, 2))
        reconstructed = self.decoder(self.concentrations)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (2, 3, 1))
        reconstructed = self.normalizer(reconstructed)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (3, 1, 2))
        return reconstructed

    @property
    def spectra(self):
        print(self.spatial_encoder[-1].conv.weight)
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class SpectralSpatialRegUnmixing(nn.Module):
    """
    Convolutional AE with a spectral dimensionality reduction and spatial regularization for unmixing.
    """
    def __init__(
        self, spectra_length: int, nb_components: int, spectral_features: Sequence[int],
        spectral_filters: Sequence[int], spectral_activations: Sequence[str], pooling_types: Sequence[str],
        pooling_sizes: Sequence[int], spatial_filters: Sequence[Union[int, Sequence[int]]],
        spatial_activations: Sequence[str], padding_modes: Sequence[str],
        normalizer: Union[nn.Module, dict] = nn.Softmax2d()
    ) -> None:
        super().__init__()
        self.spectral_blocks = []
        for feature, filter_size, activation, pooling_type, pooling_size in zip(spectral_features, spectral_filters,
                                                                                spectral_activations, pooling_types,
                                                                                pooling_sizes):
            if len(self.spectral_blocks) == 0:
                self.spectral_blocks.append(_SpectralEncoderBlock(1, feature, filter_size, activation, pooling_type,
                                                                 pooling_size))
            else:
                self.spectral_blocks.append(_SpectralEncoderBlock(self.spectral_blocks[-1].conv.out_channels, feature,
                                                                 filter_size, activation, pooling_type, pooling_size))
        self.feature_extractor = nn.Sequential(*self.spectral_blocks)
        dummy_spectra = torch.zeros((1, 1, spectra_length))
        dummy_spectra = self.feature_extractor(dummy_spectra)
        features_shape = (np.prod(dummy_spectra.shape[-2:])).item()
        self.encoder = nn.Linear(features_shape, nb_components, bias=False)
        self.spatial_blocks = []
        for filter_size, activation, padding_mode in zip(spatial_filters, spatial_activations, padding_modes):
            self.spatial_blocks.append(_SpatialEncoderBlock(nb_components, nb_components, filter_size, activation,
                                                           padding_mode, bias=False))
        self.spatial_regularizer = nn.Sequential(*self.spatial_blocks)
        if isinstance(normalizer, dict):
            normalizer = normalizer_factory(normalizer['name'], **normalizer['parameters'])
        self.normalizer = normalizer
        self.decoder = nn.Linear(nb_components, spectra_length, bias=False)
        #with torch.no_grad():
            #peaks = torch.zeros((nb_components, spectra_length))
            #for peak_idx in range(len(peaks)):
            #    center = torch.randint(spectra_length, (1,))[0]
            #    width = 10
            #    peaks[peak_idx] = 1. / (width * torch.sqrt(Tensor([2. * pi]))) * torch.exp(
            #        - (torch.arange(spectra_length) - center) ** 2 / (2. * width ** 2))
            #self.decoder.weight.copy_(peaks.T)
        self.concentrations = None

    def forward(self, x: Tensor) -> Tensor:
        linearized_shape = np.prod(x.shape[:-1]).item()
        linearized = torch.reshape(x, (linearized_shape, 1, x.shape[-1]))
        spectral_features = self.feature_extractor(linearized)
        features_concat_shape = np.prod(spectral_features.shape[-2:]).item()
        features_map = torch.reshape(spectral_features, (*x.shape[:-1], features_concat_shape))
        self.concentrations = self.encoder(features_map)
        # Need to move dimensions to have features after batch dim
        self.concentrations = torch.movedim(self.concentrations, (1, 2, 3), (2, 3, 1))
        self.concentrations = self.spatial_regularizer(self.concentrations)
        self.concentrations = self.normalizer(self.concentrations)
        # Need to move dimensions to have features at the end for Dense layer
        self.concentrations = torch.movedim(self.concentrations, (1, 2, 3), (3, 1, 2))
        reconstructed = self.decoder(self.concentrations)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (2, 3, 1))
        reconstructed = self.normalizer(reconstructed)
        reconstructed = torch.movedim(reconstructed, (1, 2, 3), (3, 1, 2))
        return reconstructed

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__


class DenseVAEUnmixing(nn.Module):
    def __init__(
        self, spectra_length: int, features: Sequence[int], activations: Optional[Sequence[str]] = None,
        init_decoder: str = 'random', reduction: str = 'sum', loss_w: float = 1.
    ) -> None:
        super().__init__()
        self.encoder = []
        for idx, feature in enumerate(features[:-1]):
            in_features = spectra_length if idx == 0 else self.encoder[-1].dense.out_features
            activation = None if activations is None else activations[idx]
            self.encoder.append(_DenseBlock(in_features, feature, activation, True))
        self.encoder = nn.Sequential(*self.encoder)
        self.mean_layer = nn.Linear(features[-2], features[-1])
        self.var_layer = nn.Linear(features[-2], features[-1])
        self.conc_normalizer = nn.Softmax(dim=-1)
        self.decoder = nn.Linear(features[-1], spectra_length, bias=False)
        if init_decoder == 'zero' or init_decoder == 'gaussian':
            with torch.no_grad():
                peaks = torch.zeros((features[-1], spectra_length))
                if init_decoder == 'gaussian':
                    for peak_idx in range(len(peaks)):
                        center = torch.randint(spectra_length, (1,))[0]
                        width = 10
                        peaks[peak_idx] = gaussian(spectra_length, center, width)
                self.decoder.weight.copy_(peaks.T)
        self.concentrations = None
        self.reduction = reduction
        self.loss_w = loss_w

    def forward(self, x: Tensor) -> Tensor:
        x = self.encoder(x)
        self.means = self.mean_layer(x)
        self.log_var = self.var_layer(x)
        std = torch.exp(0.5 * self.log_var)
        self.concentrations = torch.normal(self.means, std)
        # self.concentrations = self.conc_normalizer(self.concentrations)
        reconstructed = self.decoder(self.concentrations)

        return reconstructed

    def kl_loss(self) -> Tensor:
        loss = -0.5 * (1 + self.log_var - self.means**2 - torch.exp(self.log_var))
        if self.reduction == 'sum':
            loss = torch.sum(loss)
        elif self.reduction == 'mean':
            loss = torch.sum(loss) / np.prod(loss.shape)
        elif self.reduction == 'batchmean':
            loss = torch.sum(loss) / loss.shape[0]
        return loss*self.loss_w

    @property
    def spectra(self):
        return self.decoder.weight

    @property
    def filters(self):
        return torch.unsqueeze(torch.unsqueeze(self.decoder.weight, -1), -1)

    @property
    def name(self):
        return self.__class__.__name__