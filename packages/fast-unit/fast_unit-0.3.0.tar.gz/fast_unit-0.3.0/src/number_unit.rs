use std::cmp::min;
use std::ops::{Add, Mul, Sub};
use crate::unit_reg::current_unit_count;
use crate::UNITS;

#[derive(Clone)]
pub(crate) struct NumberUnit {
    pub(crate) u: Vec<i16>
}

impl NumberUnit {
    pub(crate) fn is_unitless(&self) -> bool {
        for i in &self.u {
            if i != &0i16 { return false }
        }
        true
    }

    pub(crate) fn add(&self, other: &NumberUnit) -> NumberUnit {
        let mut unit_vec = vec![0; current_unit_count()];
        for i in 0..self.u.len() {
            unit_vec[i] = self.u[i]
        }
        for i in 0..other.u.len() {
            unit_vec[i] += other.u[i]
        }
        NumberUnit{ u: unit_vec }
    }

    pub(crate) fn sub(&self, other: &NumberUnit) -> NumberUnit {
        let mut unit_vec = vec![0; current_unit_count()];
        for i in 0..self.u.len() {
            unit_vec[i] = self.u[i]
        }
        for i in 0..other.u.len() {
            unit_vec[i] -= other.u[i]
        }
        NumberUnit{ u: unit_vec }
    }
}

impl Mul<i32> for NumberUnit {
    type Output = Self;

    fn mul(self, rhs: i32) -> Self {
        let mut res = self.u.clone();
        for i in 0..res.len() {
            res[i] *= rhs as i16
        }
        NumberUnit{ u: res }
    }
}

impl PartialEq for NumberUnit {
    fn eq(&self, other: &Self) -> bool {
        let k = min(self.u.len(), other.u.len());
        for i in 0..k {
            if self.u[i] != other.u[i] {
                return false
            }
        }
        if self.u.len() > other.u.len() {
            for i in (k + 1)..self.u.len() {
                if self.u[i] != 0 {
                    return false
                }
            }
        } else if other.u.len() > self.u.len() {
            for i in (k + 1)..other.u.len() {
                if other.u[i] != 0 {
                    return false
                }
            }
        }
        true
    }

    fn ne(&self, other: &Self) -> bool {
        !(self == other)
    }
}

impl ToString for NumberUnit {
    fn to_string(&self) -> String {
        let mut numerator: String = "".to_string();
        let mut denominator: String = "".to_string();
        for (i, p) in self.u.iter().enumerate() {
            if *p == 0 { continue; }
            unsafe {
                let n = &UNITS.lock().unwrap()[i].name;
                if *p == 1 { numerator += n }
                else if *p == -1 { denominator += n }
                else if *p > 1 { numerator += &*(n.to_owned() + &p.to_string()) }
                else { denominator += &*(n.to_owned() + &(-p).to_string()) }
            }
        }
        return if denominator == "" {
            numerator
        } else {
            numerator + "/" + &*denominator
        }
    }
}