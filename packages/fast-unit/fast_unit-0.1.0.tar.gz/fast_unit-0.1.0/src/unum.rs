use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;

use crate::NumberUnit;
use crate::unit_reg::current_unit_count;


#[pyclass]
#[derive(Clone)]
pub(crate) struct Unum {
    pub(crate) val: f64,
    pub(crate) unit: NumberUnit
}

#[pymethods]
impl Unum {
    #[new]
    fn new(val: f64) -> Self {
        Unum { val, unit: NumberUnit{ u: vec![0; current_unit_count()] } }
    }

    fn as_number(&self, u: &Unum) -> PyResult<f64> {
        return if self.unit == u.unit {
            Ok(self.val / u.val)
        } else {
            Err(PyTypeError::new_err("Unit Mismatch"))
        }
    }


    // --- str and repr ---

    fn __str__(&self) -> PyResult<String> {
        Ok(self.val.to_string() + " [" + &*self.unit.to_string() + "]")
    }

    #[inline]
    fn __repr__(&self) -> PyResult<String> {
        self.__str__()
    }


    // --- multiplication ---

    fn __mul__(&self, other: &PyAny) -> PyResult<Unum> {
        let o = unwrap_unum(other);
        Ok(Unum {
            val: self.val * o.val,
            unit: self.unit.add(&o.unit)
        })
    }

    #[inline]
    fn __rmul__(&self, other: &PyAny) -> PyResult<Unum> {
        self.__mul__(other)
    }


    // --- division ---

    fn __div__(&self, other: &PyAny) -> PyResult<Unum> {
        let o = unwrap_unum(other);
        Ok(Unum {
            val: self.val / o.val,
            unit: self.unit.sub(&o.unit)
        })
    }

    #[inline]
    fn __truediv__(&self, other: &PyAny) -> PyResult<Unum> {
        self.__div__(other)
    }

    #[inline]
    fn __rdiv__(&self, other: &PyAny) -> PyResult<Unum> {
        self.__div__(other)
    }

    #[inline]
    fn __rtruediv__(&self, other: &PyAny) -> PyResult<Unum> {
        self.__div__(other)
    }


    // --- exponents ---

    fn __pow__(&self, power: &PyAny, _modulo: Option<u32>) -> PyResult<Unum> {
        let o = unwrap_unum(power);
        return if o.unit.is_unitless() {
            if o.val.fract() == 0f64 {
                let power_int = o.val as i32;
                Ok(Unum {
                    val: self.val.powi(power_int),
                    unit: self.unit.clone() * power_int
                })
            } else {
                Err(PyTypeError::new_err("Fractional exponent"))
            }
        } else {
            Err(PyTypeError::new_err("Should be Unitless"))
        }
    }


    // --- addition and subtraction ---

    fn __add__(&self, other: &Unum) -> PyResult<Unum> {
        return if self.unit == other.unit {
            Ok(Unum {
                val: self.val + other.val,
                unit: self.unit.clone()
            })
        } else {
            Err(PyTypeError::new_err("Unit Mismatch"))
        }
    }

    fn __sub__(&self, other: &Unum) -> PyResult<Unum> {
        return if self.unit == other.unit {
            Ok(Unum {
                val: self.val - other.val,
                unit: self.unit.clone()
            })
        } else {
            Err(PyTypeError::new_err("Unit Mismatch"))
        }
    }


    // --- positive and negative ---

    fn __pos__(&self) -> PyResult<Unum> {
        Ok(self.clone())
    }

    fn __neg__(&self) -> PyResult<Unum> {
        Ok(Unum {
            val: -self.val,
            unit: self.unit.clone()
        })
    }


    // --- math functions ---

    fn __abs__(&self) -> PyResult<Unum> {
        Ok(Unum {
            val: self.val.abs(),
            unit: self.unit.clone()
        })
    }


    // -- in place operators ---

    fn __iadd__(&mut self, other: &Unum) -> PyResult<()> {
        return if self.unit == other.unit {
            self.val += other.val;
            Ok(())
        } else {
            Err(PyTypeError::new_err("Unit Mismatch"))
        }
    }

    fn __isub__(&mut self, other: &Unum) -> PyResult<()> {
        return if self.unit == other.unit {
            self.val += other.val;
            Ok(())
        } else {
            Err(PyTypeError::new_err("Unit Mismatch"))
        }
    }

    fn __imul__(&mut self, other: &PyAny) -> PyResult<()> {
        let o = unwrap_unum(other);
        self.val *= o.val;
        self.unit = self.unit.add(&o.unit);  // TODO make this in-place??
        Ok(())
    }

    fn __idiv__(&mut self, other: &PyAny) -> PyResult<()> {
        let o = unwrap_unum(other);
        self.val /= o.val;
        self.unit = self.unit.sub(&o.unit);  // TODO make this in-place??
        Ok(())
    }

    #[inline]
    fn __itruediv__(&mut self, other: &PyAny) -> PyResult<()> {
        self.__idiv__(other)
    }

    fn __ipow__(&mut self, power: &PyAny, _modulo: Option<u32>) -> PyResult<()> {
        let o = unwrap_unum(power);
        return if o.unit.is_unitless() {
            if o.val.fract() == 0f64 {
                let power_int = o.val as i32;
                self.val = self.val.powi(power_int);
                self.unit = self.unit.clone() * power_int;
                Ok(())
            } else {
                Err(PyTypeError::new_err("Fractional exponent"))
            }
        } else {
            Err(PyTypeError::new_err("Should be Unitless"))
        }
    }
}

#[inline]
fn unwrap_unum(obj: &PyAny) -> Unum {
    match obj.extract() {
        Ok(u) => u,
        Err(_) => {
            Unum {
                val: obj.extract().unwrap(),
                unit: NumberUnit{ u: vec![] }
            }
        }
    }
}
