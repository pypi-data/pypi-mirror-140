from trame import state, get_cli_parser, controller as ctrl
from . import engine


def on_start():
    parser = get_cli_parser()
    parser.add_argument("--data", help="Path to trained AI model", dest="data")

    # Add model path be part of state
    state.path_to_model = parser.parse_known_args()[0].data
    ctrl.on_ready = engine.initialize
