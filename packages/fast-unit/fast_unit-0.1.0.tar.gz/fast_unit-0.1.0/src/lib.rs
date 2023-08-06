#![feature(once_cell)]
use pyo3::prelude::*;

mod number_unit;
use number_unit::NumberUnit;

mod unit_reg;
use unit_reg::UNITS;

mod unum;
use unum::Unum;
use unit_reg::BaseUnit;

#[pyfunction]
pub(crate) fn add_unit(name: String, long_name: String) -> PyResult<Unum> {
    let len: usize;

    unsafe {
        let mut units = UNITS.lock().unwrap();
        units.push(BaseUnit { name, long_name });
        len = units.len()
    }

    let mut u = vec![0; len];
    u[len - 1] = 1;

    Ok(
        Unum {
            val: 1f64,
            unit: NumberUnit {
                u
            }
        }
    )
}

#[pymodule]
fn fast_unit(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Unum>()?;
    m.add_function(wrap_pyfunction!(add_unit, m)?)?;

    Ok(())
}
