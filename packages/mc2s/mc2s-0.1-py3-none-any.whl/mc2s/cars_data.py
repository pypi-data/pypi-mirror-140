import os
from pathlib import Path
from typing import List, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from carsdata.utils.metrics import Metric, metric_factory
from carsdata.utils.plot import plot_curves, plot_mat
from carsdata.utils.types import ColorMap
from carsdata.utils.color_maps import RedColorMap, cmap_factory
from carsdata.utils.data import Data, DataFile, data_factory
from carsdata.utils.files import get_data_files, read_json
from carsdata.utils.math import sum_norm
from carsdata.analyze.analyzer import Analyzer
from carsdata.analyze.factory import analyzer_factory


class CARSData:
    """The CARSData application. Construct it with chosen parameters and use run to launch the data analysis.
    """
    _data: List[Data]
    _analyzer: Analyzer
    _reconstruted_metrics: Optional[List[Metric]]
    color_map: ColorMap
    x_label: Optional[str]
    y_label: Optional[str]
    vspan: Optional[List[dict]]
    spectra_colors: Optional[List[str]]
    separe_spectra: bool
    colorbar: bool
    results_dir: Optional[str]
    show: bool

    def __init__(
        self, data: List[Union[Data, str, dict, List[str]]], analyzer: Union[Analyzer, dict],
        reconstructed_metrics: Optional[List[Union[Metric, dict]]] = None,
        color_map: Union[ColorMap, dict] = RedColorMap(), x_label: Optional[str] = 'Raman shift (cm$^{-1}$)',
        y_label: Optional[str] = 'Intensity (a.u.)', vspan: Optional[List[dict]] = None,
        spectra_colors: List[str] = None, separe_spectra: bool = False, colorbar: bool = False,
        results_dir: Optional[str] = None, show: bool = True,
    ) -> None:
        # Init data
        data_list = []
        for data_line in data:
            if isinstance(data_line, dict):
                data_list.append(data_factory(data_line['name'], **data_line['parameters']))
            elif isinstance(data_line, str):
                if os.path.isdir(data_line):
                    file_list = get_data_files(data_line)
                    for file in file_list:
                        data_list.append(DataFile(file))
                else:
                    data_list.append(DataFile(data_line))
            elif isinstance(data_line, list):
                files_list = []
                for path in data_line:
                    if os.path.isdir(path):
                        dir_files = get_data_files(path)
                        for file in dir_files:
                            files_list.append(file)
                    else:
                        files_list.append(path)
                data_list.append(DataFile(files_list))
            else:
                data_list.append(data_line)
        # Init analyzer
        if isinstance(analyzer, dict):
            analyzer = analyzer_factory(analyzer['name'], **analyzer['parameters'])
        # Init metrics
        if reconstructed_metrics is not None:
            for metric_idx, metric in enumerate(reconstructed_metrics):
                if isinstance(metric, dict):
                    reconstructed_metrics[metric_idx] = metric_factory(metric['name'], **metric['parameters'])
        # Init color map
        if isinstance(color_map, dict):
            color_map = cmap_factory(color_map['name'], **color_map['parameters'])
        # Init attributes
        self._data = data_list
        self._analyzer = analyzer
        self._reconstructed_metrics = reconstructed_metrics
        self.color_map = color_map
        self.x_label = x_label
        self.y_label = y_label
        self.vspan = vspan
        self.spectra_colors = spectra_colors
        self.separe_spectra = separe_spectra
        self.colorbar = colorbar
        self.results_dir = results_dir
        self.show = show
    
    def run(self) -> None:
        for idx, data_elem in enumerate(self._data):
            data_elem.load()
            result = self._analyzer.analyze(data_elem)
            result_folder = None
            if self.results_dir is not None:
                result_folder = os.path.join(self.results_dir, str(idx))
            self.plot_and_write_results(data_elem, result, result_folder)
    
    def plot_and_write_results(self, data: Data, result: np.ndarray, result_directory: Optional[str] = None) -> None:
        if result_directory is not None:
            Path(result_directory).mkdir(parents=True, exist_ok=True)
            np.savetxt(os.path.join(result_directory, 'spectral_units.txt'), data.spectral_units)
        error = getattr(self._analyzer, 'error', None)
        if len(result.shape) > 3:
            for layer_id, layer in enumerate(result):
                layer_dir = None
                if result_directory is not None:
                    layer_dir = os.path.join(result_directory, f'slice_{layer_id}')
                    Path(layer_dir).mkdir(parents=True, exist_ok=True)
                    self.write_layer_files(layer, data.measures[layer_id], data.pos[layer_id], layer_dir)
                self.plot_and_write_dims(layer, layer_id, layer_dir)
                if error is not None:
                    self.plot_and_write_error(error[layer_id], layer_id, layer_dir)
        else:
            if result_directory is not None:
                self.write_layer_files(result, data.measures, data.pos, result_directory)
            self.plot_and_write_dims(result, 0, result_directory)
            if error is not None:
                self.plot_and_write_error(error, 0, result_directory)
        spectra = getattr(self._analyzer, 'spectra', None)
        if self._reconstructed_metrics is not None and spectra is not None:
            reconstructed = result @  spectra.T
            for metric in self._reconstructed_metrics:
                name = metric.__class__.__name__
                if name == 'KLDiv':
                    input = sum_norm(data.measures, -1)
                    output = sum_norm(reconstructed, -1)
                    res = metric.compute(input, output)
                else:
                    res = metric.compute(data.measures, reconstructed)
                if self.show:
                    print(f'{name}: {res}')
                if result_directory is not None:
                    np.savetxt(os.path.join(result_directory, f'{name}.txt'), [res])
        if spectra is not None:
            self.plot_and_write_spectra(spectra, data.spectral_units, result_directory)
        if self.show:
            plt.show()

    def write_layer_files(self, result: np.ndarray, data: np.ndarray, pos: np.ndarray, directory: str) -> None:
        np.savetxt(os.path.join(directory, 'result.txt'), result.reshape(result.shape[0]*result.shape[1], result.shape[2]))
        np.savetxt(os.path.join(directory, 'data.txt'), data.reshape(data.shape[0]*data.shape[1], data.shape[2]))
        np.savetxt(os.path.join(directory, 'pos.txt'), pos.reshape(pos.shape[0]*pos.shape[1], pos.shape[2]))

    def plot_and_write_dims(self, data: np.ndarray, layer: int, directory: Optional[str] = None) -> None:
        for idx in range(data.shape[-1]):
            image = data[..., idx]
            if directory is not None:
                im = Image.fromarray(image)
                tif_file = os.path.join(directory, 'dim_' + str(idx + 1) + '.tif')
                im.save(tif_file)
            fig = plot_mat(image, cmap=self.color_map, colorbar=self.colorbar)
            if directory is not None:
                fig.set_tight_layout(True)
                file_path = os.path.join(directory, 'dim_' + str(idx + 1) + '.png')
                if self.colorbar:
                    fig.savefig(file_path)
                else:
                    plt.imsave(file_path, image, cmap=self.color_map)
                plt.close(fig)

    def plot_and_write_error(self, error: np.ndarray, layer: int, directory: Optional[str] = None) -> None:
        abs_err = np.abs(error)
        err_abs_mean = np.mean(abs_err, -1)
        err_abs_std = np.std(abs_err, -1)
        fig_abs_mean = plot_mat(err_abs_mean, cmap=self.color_map, colorbar=self.colorbar)
        fig_abs_std = plot_mat(err_abs_std, cmap=self.color_map, colorbar=self.colorbar)
        if directory is not None:
            fig_abs_mean.set_tight_layout(True)
            file_path = os.path.join(directory, 'abs_error_mean.png')
            if self.colorbar:
                fig_abs_mean.savefig(file_path)
            else:
                plt.imsave(file_path, err_abs_mean, cmap=self.color_map)
            plt.close(fig_abs_mean)
            fig_abs_std.set_tight_layout(True)
            file_path = os.path.join(directory, 'abs_error_std.png')
            if self.colorbar:
                fig_abs_std.savefig(file_path)
            else:
                plt.imsave(file_path, err_abs_std, cmap=self.color_map)
            plt.close(fig_abs_std)

    def plot_and_write_spectra(
        self, spectra: np.ndarray, spectral_units: np.ndarray, directory: Optional[str] = None
    ) -> None:
        abs_spectral_units = np.abs(spectral_units)
        if self.separe_spectra:
            for spectr_idx in range(spectra.shape[-1]):
                spectra_fig = plot_curves(abs_spectral_units, spectra[..., spectr_idx], x_label=self.x_label,
                                          y_label=self.y_label,  vspan=self.vspan,colors=self.spectra_colors)
                if directory is not None:
                    spectra_fig.set_tight_layout(True)
                    file_path = os.path.join(directory, f'spectrum_{spectr_idx+1}.png')
                    spectra_fig.savefig(file_path)
                    plt.close(spectra_fig)
        else:
            normalized_spectra = np.zeros(spectra.shape)
            for idx, spectr in enumerate(spectra.T):
                min_value = spectr.min()
                max_value = spectr.max()
                max_previous = normalized_spectra[:, idx-1].max() if idx != 0 else 0
                normalized_spectra[:, idx] = (spectr-min_value)/(max_value-min_value)+(max_previous+0.1)
            legend = [str(idx+1) for idx in range(spectra.shape[1])]

            spectra_fig = plot_curves(abs_spectral_units, spectra, 'Spectra', legend, x_label=self.x_label,
                                      y_label=self.y_label, vspan=self.vspan, colors=self.spectra_colors)
            norm_spectra_fig = plot_curves(abs_spectral_units, normalized_spectra, 'Normalized spectra', legend,
                                           x_label=self.x_label, y_label=self.y_label, vspan=self.vspan,
                                           colors=self.spectra_colors)

            if directory is not None:
                spectra_fig.set_tight_layout(True)
                file_path = os.path.join(directory, 'spectra.png')
                spectra_fig.savefig(file_path)
                plt.close(spectra_fig)
                norm_spectra_fig.set_tight_layout(True)
                file_path = os.path.join(directory, 'normalized_spectra.png')
                norm_spectra_fig.savefig(file_path)
                plt.close(norm_spectra_fig)
                np.savetxt(os.path.join(directory, 'spectra.txt'), spectra)
