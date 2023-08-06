from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class ViewMatrix(Function):
    """Calculate view matrix for a receiver file."""

    radiance_parameters = Inputs.str(
        description='Radiance parameters. -I, -c 1 and -aa 0 are already included in '
        'the command.', default=''
    )

    fixed_radiance_parameters = Inputs.str(
        description='Radiance parameters. -I, -c 1 and -aa 0 are already included in '
        'the command.', default='-aa 0 -I -c 1'
    )

    sensor_count = Inputs.int(
        description='Minimum number of sensors in each generated grid.',
        spec={'type': 'integer', 'minimum': 1}
    )

    receiver_file = Inputs.file(
        description='Path to a receiver file.', path='receiver.rad',
        extensions=['rad']
    )

    sensor_grid = Inputs.file(
        description='Path to sensor grid files.', path='grid.pts',
        extensions=['pts']
    )

    scene_file = Inputs.file(
        description='Path to an octree file to describe the scene.', path='scene.oct',
        extensions=['oct']
    )

    receivers_folder = Inputs.folder(
        description='Folder containing any receiver files needed for ray tracing. '
        'This folder is usually the aperture group folder inside the model folder.',
        path='model/aperture_group'
    )

    bsdf_folder = Inputs.folder(
        description='Folder containing any BSDF files needed for ray tracing.',
        path='model/bsdf', optional=True
    )

    @command
    def run_view_mtx(self):
        return 'honeybee-radiance multi-phase view-matrix receiver.rad scene.oct ' \
            'grid.pts --sensor-count {{self.sensor_count}} ' \
            '--rad-params "{{self.radiance_parameters}}" --rad-params-locked ' \
            '"{{self.fixed_radiance_parameters}}"'

    view_mtx = Outputs.folder(
        description='Output view matrix folder.', path='vmtx'
    )


@dataclass
class FluxTransfer(Function):
    """Calculate flux transfer matrix between a sender and a receiver file."""

    radiance_parameters = Inputs.str(
        description='Radiance parameters. -aa 0 is already included in '
        'the command. Note that -c should not be 1.', default=''
    )

    fixed_radiance_parameters = Inputs.str(
        description='Radiance parameters.'
        'the command.', default='-aa 0'
    )

    receiver_file = Inputs.file(
        description='Path to a receiver file.', path='receiver.rad',
        extensions=['rad']
    )

    sender_file = Inputs.file(
        description='Path to sender file.', path='sender.rad',
        extensions=['rad']
    )

    senders_folder = Inputs.folder(
        description='Folder containing any senders files needed for ray tracing. '
        'This folder is usually the aperture group folder inside the model folder.',
        path='model/aperture_group'
    )

    scene_file = Inputs.file(
        description='Path to an octree file to describe the scene.', path='scene.oct',
        extensions=['oct']
    )

    bsdf_folder = Inputs.folder(
        description='Folder containing any BSDF files needed for ray tracing.',
        path='model/bsdf', optional=True
    )

    @command
    def run_flux_mtx(self):
        return 'honeybee-radiance multi-phase flux-transfer sender.rad receiver.rad ' \
               'scene.oct  --output output.dmx ' \
            '--rad-params "{{self.radiance_parameters}}" --rad-params-locked '\
            '"{{self.fixed_radiance_parameters}}"'

    flux_mtx = Outputs.file(
        description='Output daylight matrix file.', path='output.dmx'
    )


@dataclass
class MultiPhaseCombinations(Function):
    """Create two JSON files for multiplication combinations and results mapper."""

    sender_info = Inputs.file(
        description='Path to a JSON file that includes the information for senders. '
        'This file is created as an output of the daylight matrix grouping command.',
        path='sender_info.json', extensions=['json']
    )

    receiver_info = Inputs.file(
        description='Path to a JSON file that includes the information for receivers. '
        'This file is written to model/receiver folder.',
        path='receiver_info.json', extensions=['json']
    )

    states_info = Inputs.file(
        description='Path to a JSON file that includes the state information for all '
        'the aperture groups. This file is created under model/aperture_groups.',
        path='states_info.json', extensions=['json']
    )

    @command
    def calculate_multiphase_combs(self):
        return 'honeybee-radiance multi-phase three-phase combinations ' \
            'sender_info.json receiver_info.json states_info.json --folder combs ' \
            '-rn 3phase_results_info -cn 3phase_multiplication_info'

    multiplication_file = Outputs.file(
        description='The combination of matrix multiplication for 3 Phase studies.',
        path='combs/3phase_multiplication_info.json'
    )

    multiplication_info = Outputs.list(
        description='The combination of matrix multiplication for 3 Phase studies.',
        path='combs/3phase_multiplication_info.json'
    )

    results_mapper = Outputs.file(
        description='Results mapper for each sensor grid in the model.',
        path='combs/3phase_results_info.json'
    )


@dataclass
class DaylightMatrixGrouping(Function):
    """Group apertures for daylight matrix."""

    model_folder = Inputs.folder(
        description='Radiance model folder', path='model'
    )

    scene_file = Inputs.file(
        description='Path to an octree file to describe the scene.', path='scene.oct',
        extensions=['oct']
    )

    sky_dome = Inputs.file(
        description='Path to rflux sky file.', path='sky.dome'
    )

    size = Inputs.float(
        description='Aperture grid size. A lower number will give a finer grid and more '
        'accurate results but the calculation time will increase.', default=0.2
    )

    threshold = Inputs.float(
        description='A number that determines if two apertures/aperture groups can be '
        'clustered. A higher number is more accurate but will also increase the number '
        'of aperture groups', default=0.001
    )

    ambient_division = Inputs.int(
        description='Number of ambient divisions (-ad) for view factor calculation in '
        'rfluxmtx. Increasing the number will give more accurate results but also '
        'increase the calculation time.', default=1000
    )

    @command
    def group_apertures(self):
        return 'honeybee-radiance multi-phase dmtx-group model scene.oct sky.dome ' \
            '--output-folder output --name _info --size {{self.size}} ' \
            '--threshold {{self.threshold}} --ambient-division {{self.ambient_division}}'

    grouped_apertures_folder = Outputs.folder(
        description='Output folder to grouped apertures.',
        path='output/groups'
    )

    grouped_apertures = Outputs.list(
        description='List of names for grouped apertures.',
        path='output/groups/_info.json'
    )

    grouped_apertures_file = Outputs.file(
        description='Grouped apertures information file.',
        path='output/groups/_info.json'
    )
