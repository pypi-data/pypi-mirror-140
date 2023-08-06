from .xai.ml import RegressionPressure
from .xai import get_xai_method, is_method_sensitive_to_xy, update_full_pipeline
from .xai.colors import lutPerm, lutPress

from trame import state, GoogleDriveFile

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

ai_model = None

state.update(
    {
        "steps": ["Conv 2D", "Relu", "Max Pool", "Drop-out", "Dense", "XAI"],
        # XAI methods
        "xaiPreset": "erdc_rainbow_bright",
        "xaiHover": None,
        "xaiOutputSelected": -1,
        # Weights
        "weightsInputs": None,
        "weightsOutputs": [],
        # LookupTables configurations
        "lutPerm": lutPerm,
        "lutPress": lutPress,
    }
)

# -----------------------------------------------------------------------------
# XAI
# -----------------------------------------------------------------------------

BC_MODES = {
    "initial": [25, 25],
    "wet-wet": [45, 45],
    "wet-dry": [45, 5],
    "dry-wet": [5, 45],
    "dry-dry": [5, 5],
    "drew-drew": [10, 10],
}

# -----------------------------------------------------------------------------


@state.change("mode")
def update_ai(mode, **kwargs):
    left, right = BC_MODES[mode]
    ai_model.set_bc(left, right)
    state.aiInputPerm = ai_model.permeability()
    state.aiInputPress = ai_model.pressure()
    state.aiOutputPress = ai_model.predict()
    xai()
    update_full_pipeline(ai_model)


# -----------------------------------------------------------------------------


@state.change("xaiHover", "mode", "xaiMethod", "step", "xaiModifier")
def xai(**kwargs):
    ij, step = state.xaiHover, state.step
    # prev_result = app.get('xaiOutputs')
    method = get_xai_method()
    xy_dep = is_method_sensitive_to_xy(method)
    if xy_dep and ij:
        xy = (ij["i"], ij["j"])
        state.xaiOutputs = ai_model.explain(method, xy)
    elif not xy_dep:
        # print('b')
        # if prev_result is None:
        #   print(' => in')
        state.xaiOutputs = ai_model.explain(method, (-1, -1))
    else:
        state.xaiOutputs = None

    if step == 5 and ij:
        state.weightsOutputs = ai_model.get_dense_weights(**ij)
    else:
        state.weightsOutputs = []


# -----------------------------------------------------------------------------


@state.change("xaiOutputSelected")
def update_active_weights(step, xaiOutputSelected, **kwargs):
    idx = xaiOutputSelected

    if step in [1, 2, 3]:
        state.weightsInputs = ai_model.get_weights(idx)
    else:
        state.weightsInputs = None


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------


def initialize(path_to_model, mode, **kwargs):
    print("xai engine initialize", path_to_model, mode)
    global ai_model
    if path_to_model:
        ai_model = RegressionPressure(path_to_model)
    else:
        remote_model = GoogleDriveFile(
            local_path="./refs/default-trained-model.out",
            google_id="1AL2KlhfH_ZcQJM8wWSb9pG9M_jxgcn50",
            local_base=__file__,
        )
        ai_model = RegressionPressure(remote_model.path)
    update_ai(mode)
