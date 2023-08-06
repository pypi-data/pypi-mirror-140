Motion correction in two-channel calcium imaging

This is a python package implementing the additive inference model (AIM).

The model can be called simply with
import additive_inference_model.calcium_inference_models as cim
trained_variables = cim.gp_model_additive_fft_circ(red, green)

NOTE: The red and green channel cannot have nans and should be adjusted for photobleaching. This is normally achieved by fitting exp(-t / tau) to the data where tau is shared across all neurons and then dividing each time trace by this exponential.

To see an example on synthetic data, look at examples/run_AIM_on_synthetic_data.py


