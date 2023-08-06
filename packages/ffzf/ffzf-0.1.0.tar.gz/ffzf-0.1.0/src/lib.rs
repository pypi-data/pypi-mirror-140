mod scorer;
mod finder;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use scorer::*;
use finder::*;

#[pymodule]
fn ffzf(py: Python, m: &PyModule) -> PyResult<()> {
    let scorers_module = PyModule::new(py, "scorers")?;
    scorers_module.add_wrapped(wrap_pyfunction!(levenshtein_distance))?;
    scorers_module.add_wrapped(wrap_pyfunction!(hamming_distance))?;
    scorers_module.add_wrapped(wrap_pyfunction!(jaro_similarity))?;
    scorers_module.add_wrapped(wrap_pyfunction!(jaro_winkler_similarity))?;
    let finders_module = PyModule::new(py, "finders")?;
    finders_module.add_wrapped(wrap_pyfunction!(closest))?;
    finders_module.add_wrapped(wrap_pyfunction!(n_closest))?;
    m.add_submodule(scorers_module)?;
    m.add_submodule(finders_module)?;
    
    // work around for bug registering submdules (https://github.com/PyO3/pyo3/issues/759)
    let mods = py.import("sys")?
        .getattr("modules")?;
    mods.set_item("ffzf.scorers", scorers_module)?;
    mods.set_item("ffzf.finders", finders_module)?;
    Ok(())
}


