use std::{lazy::Lazy, sync::Mutex};

pub(crate) struct BaseUnit {
    pub(crate) name: String,
    pub(crate) long_name: String
}

pub(crate) static mut UNITS: Lazy<Mutex<Vec<BaseUnit>>> = Lazy::new(|| Mutex::new(vec![]));

pub(crate) fn current_unit_count() -> usize {
    unsafe {
        *&UNITS.lock().unwrap().len()
    }
}
