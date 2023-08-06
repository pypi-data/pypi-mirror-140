from trame import controller as ctrl
from trame.layouts import FullScreenPage
from trame.html import vuetify

from . import parflow, ai, xai

# Create single page layout type
layout = FullScreenPage(
    "Sandtank ML",
    on_ready=ctrl.on_ready,
)

# Main content
with layout.root:
    with vuetify.VContainer(fluid=True, classes="pa-0") as container:
        parflow.create_control_panel(container)
        ai.create_control_panel(container)
        xai.create_control_panel(container)

        # Dev reload
        with vuetify.VBtn(
            icon=True,
            small=True,
            elevation=0,
            outlined=True,
            click="trigger('server_reload')",
            style="position: absolute; right: 5px; bottom: 5px;",
        ):
            vuetify.VIcon("mdi-autorenew")
